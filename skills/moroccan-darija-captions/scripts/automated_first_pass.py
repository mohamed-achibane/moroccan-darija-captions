#!/usr/bin/env python3
"""Compare flagged transcript spans with an authorized OpenAI ASR pass.

Writes candidate wording and sequence-comparison evidence to a new private
directory. It never edits the input transcript or claims a human reviewed audio.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import unicodedata
import uuid
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:  # Use the platform certificate store when certifi is absent.
    certifi = None


TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a private ASR comparison for low-confidence transcript spans."
    )
    parser.add_argument("--transcript", required=True, type=Path, help="Transcript JSON with a words array")
    parser.add_argument("--audio", required=True, type=Path, help="Source audio or video file")
    parser.add_argument("--output", required=True, type=Path, help="New private output directory outside the source project")
    parser.add_argument("--model", default="gpt-4o-transcribe", help="Authorized OpenAI transcription model")
    parser.add_argument("--confidence-field", default="alignmentScore", help="Word score field used for flags")
    parser.add_argument("--flag-below", type=float, default=0.5, help="Flag scores below this value; not an accuracy cutoff")
    parser.add_argument("--padding", type=float, default=1.2, help="Seconds of context around each phrase")
    parser.add_argument("--merge-gap", type=float, default=0.5, help="Merge flagged windows separated by at most this many seconds")
    parser.add_argument("--estimated-cost-usd", required=True, type=float, help="Estimate from current official provider pricing")
    parser.add_argument("--max-cost-usd", required=True, type=float, help="User-authorized cost ceiling for this pass")
    parser.add_argument(
        "--authorize-openai-upload",
        required=True,
        choices=("yes",),
        help="Required explicit marker; use only after the user authorizes this provider upload and cost.",
    )
    return parser.parse_args()


def word_groups(transcript: dict[str, Any], words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups = transcript.get("phraseGroups") or transcript.get("groups") or []
    if groups:
        return groups
    by_group: dict[int, list[int]] = {}
    for position, word in enumerate(words):
        group = word.get("phraseGroup")
        if isinstance(group, int):
            by_group.setdefault(group, []).append(int(word.get("index", position)))
    return [{"index": key, "wordIndexes": indexes} for key, indexes in sorted(by_group.items())]


def find_flagged_groups(
    transcript: dict[str, Any], words: list[dict[str, Any]], score_field: str, threshold: float
) -> tuple[list[dict[str, Any]], set[int]]:
    indexed = {int(word.get("index", position)): word for position, word in enumerate(words)}
    flagged: set[int] = set()
    for position, word in enumerate(words):
        index = int(word.get("index", position))
        score = word.get(score_field)
        start, end = float(word["start"]), float(word["end"])
        duration = transcript.get("durationSeconds", transcript.get("duration"))
        invalid_time = start < 0 or end <= start or (duration is not None and end > float(duration))
        if invalid_time or (isinstance(score, (int, float)) and score < threshold):
            flagged.add(index)

    selected = []
    for position, group in enumerate(word_groups(transcript, words)):
        indexes = group.get("wordIndexes") or group.get("wordIndices") or group.get("word_indices") or []
        indexes = [int(index) for index in indexes if int(index) in indexed]
        affected = [index for index in indexes if index in flagged]
        if not affected:
            continue
        group_words = [indexed[index] for index in indexes]
        selected.append(
            {
                "groupIndex": int(group.get("index", position)),
                "wordIndexes": indexes,
                "flaggedWordIndexes": affected,
                "start": min(float(word["start"]) for word in group_words),
                "end": max(float(word["end"]) for word in group_words),
            }
        )
    return selected, flagged


def make_windows(groups: list[dict[str, Any]], duration: float, padding: float, merge_gap: float) -> list[dict[str, Any]]:
    expanded = sorted(
        (
            {**group, "windowStart": max(0.0, group["start"] - padding), "windowEnd": min(duration, group["end"] + padding)}
            for group in groups
        ),
        key=lambda group: group["windowStart"],
    )
    windows: list[dict[str, Any]] = []
    for group in expanded:
        if windows and group["windowStart"] - windows[-1]["end"] <= merge_gap:
            windows[-1]["end"] = max(windows[-1]["end"], group["windowEnd"])
            windows[-1]["groups"].append(group)
        else:
            windows.append({"start": group["windowStart"], "end": group["windowEnd"], "groups": [group]})
    return windows


def words_from_text(text: str) -> list[str]:
    return [match.group(0) for match in TOKEN_RE.finditer(text)]


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = "".join(char for char in value if not unicodedata.category(char).startswith("M") and char != "ـ")
    return "".join(char for char in value if char.isalnum() or char in "'’")


def compare_words(source: list[dict[str, Any]], candidate: list[str]) -> dict[str, Any]:
    expected = [normalize(str(word.get("text", ""))) for word in source]
    actual = [normalize(word) for word in candidate]
    matcher = SequenceMatcher(a=expected, b=actual, autojunk=False)
    pairs: dict[int, int] = {}
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                pairs[i1 + offset] = j1 + offset
    return {
        "matches": pairs,
        "ratio": round(matcher.ratio(), 4),
        "matchingWords": len(pairs),
        "sourceWords": len(source),
        "candidateWords": len(candidate),
    }


def multipart(fields: list[tuple[str, str]], filename: str, media: bytes, boundary: str) -> bytes:
    delimiter = f"--{boundary}".encode()
    media_type = "audio/wav" if filename.casefold().endswith(".wav") else "audio/mpeg"
    chunks: list[bytes] = []
    for name, value in fields:
        chunks.extend([delimiter, f'Content-Disposition: form-data; name="{name}"'.encode(), b"", value.encode()])
    chunks.extend(
        [
            delimiter,
            f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode(),
            f"Content-Type: {media_type}".encode(),
            b"",
            media,
            delimiter + b"--",
            b"",
        ]
    )
    return b"\r\n".join(chunks)


def transcribe(key: str, clip: Path, model: str) -> dict[str, Any]:
    boundary = f"codex-{uuid.uuid4().hex}"
    fields = [
        ("model", model),
        ("response_format", "json"),
        ("temperature", "0"),
        (
            "prompt",
            "Transcribe every audible word verbatim. The speech may switch between Moroccan Darija, French, "
            "and English. Keep Darija in Arabic script and French or English in Latin script. Preserve fillers, "
            "repetitions, false starts, names, and punctuation. Do not translate, normalize, or guess unclear speech.",
        ),
    ]
    request = Request(
        "https://api.openai.com/v1/audio/transcriptions",
        data=multipart(fields, clip.name, clip.read_bytes(), boundary),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    context = ssl.create_default_context(cafile=certifi.where()) if certifi else ssl.create_default_context()
    try:
        with urlopen(request, timeout=600, context=context) as response:
            result = json.loads(response.read())
    except HTTPError as error:
        raise RuntimeError(f"OpenAI transcription failed with HTTP {error.code}; response details withheld") from None
    except URLError as error:
        raise RuntimeError(f"OpenAI transcription failed due to {type(error.reason).__name__}; details withheld") from None
    if not isinstance(result, dict) or not isinstance(result.get("text"), str):
        raise RuntimeError("OpenAI response did not contain transcript text; response details withheld")
    return result


def extract_full_audio(ffmpeg: str, source: Path, audio_output: Path) -> None:
    result = subprocess.run(
        [
            ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(source), "-map", "0:a:0", "-vn", "-c:a", "pcm_s16le", str(audio_output),
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("FFmpeg could not extract the source audio; details withheld")


def extract_clip(ffmpeg: str, source_audio: Path, clip: Path, start: float, end: float) -> None:
    result = subprocess.run(
        [
            ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(source_audio), "-ss", f"{start:.3f}", "-t", f"{end-start:.3f}",
            "-map", "0:a:0", "-vn", "-c:a", "pcm_s16le", str(clip),
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("FFmpeg could not cut a flagged audio window; details withheld")


def transcript_project_root(transcript_path: Path) -> Path:
    if transcript_path.parent.name.casefold() in {"captions", "transcripts"}:
        return transcript_path.parent.parent
    return transcript_path.parent


def main() -> int:
    args = parse_args()
    transcript_path = args.transcript.resolve()
    audio_path = args.audio.resolve()
    output = args.output.resolve()
    if not transcript_path.is_file() or not audio_path.is_file():
        print("Transcript or audio path does not exist", file=sys.stderr)
        return 2
    if args.padding < 0 or args.merge_gap < 0 or args.flag_below < 0:
        print("Padding, merge gap, and score threshold must be non-negative", file=sys.stderr)
        return 2
    if args.estimated_cost_usd < 0 or args.max_cost_usd < 0 or args.estimated_cost_usd > args.max_cost_usd:
        print("Estimated cost exceeds the user-authorized ceiling", file=sys.stderr)
        return 2
    try:
        output.relative_to(transcript_project_root(transcript_path))
    except ValueError:
        pass
    else:
        print("Output must be outside the source project", file=sys.stderr)
        return 2
    if output.exists():
        print("Output directory already exists; choose a new private folder", file=sys.stderr)
        return 2
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("Authorized OpenAI credential is unavailable; no upload was made", file=sys.stderr)
        return 2
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("FFmpeg is required to extract the flagged audio windows", file=sys.stderr)
        return 2

    document = json.loads(transcript_path.read_text(encoding="utf-8"))
    words = document.get("words")
    if not isinstance(words, list) or not words:
        print("Transcript must contain a non-empty words array", file=sys.stderr)
        return 2
    duration_value = document.get("durationSeconds", document.get("duration"))
    duration = float(duration_value) if duration_value is not None else max(float(word["end"]) for word in words)
    groups, flagged = find_flagged_groups(document, words, args.confidence_field, args.flag_below)
    windows = make_windows(groups, duration, args.padding, args.merge_gap)
    if not windows:
        print("No flagged phrase windows were found; no API request was made")
        return 0

    upload_seconds = sum(window["end"] - window["start"] for window in windows)
    output.mkdir(parents=True)
    clip_dir = output / "windows"
    clip_dir.mkdir()
    normalized_audio = output / "full-audio.wav"
    extract_full_audio(ffmpeg, audio_path, normalized_audio)
    rows = []
    for position, window in enumerate(windows):
        clip = clip_dir / f"window-{position:03d}.wav"
        extract_clip(ffmpeg, normalized_audio, clip, window["start"], window["end"])
        if clip.stat().st_size > 25 * 1024 * 1024:
            raise RuntimeError("A flagged audio window exceeds the documented upload file limit; no request was made for it")
        response = transcribe(key, clip, args.model)
        response_path = clip_dir / f"window-{position:03d}-response.json"
        response_path.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        candidate_words = words_from_text(response["text"])
        source_indexes = [
            int(word.get("index", index))
            for index, word in enumerate(words)
            if window["start"] <= (float(word["start"]) + float(word["end"])) / 2 < window["end"]
        ]
        source_words = [next(word for position, word in enumerate(words) if int(word.get("index", position)) == index) for index in source_indexes]
        comparison = compare_words(source_words, candidate_words)
        group_rows = []
        for group in window["groups"]:
            indexes = group["wordIndexes"]
            local_positions = [source_indexes.index(index) for index in indexes if index in source_indexes]
            matched_positions = [position for position in local_positions if position in comparison["matches"]]
            candidate_indexes = [comparison["matches"][position] for position in matched_positions]
            exact = (
                len(local_positions) == len(indexes)
                and len(matched_positions) == len(indexes)
                and all(candidate_indexes[offset] + 1 == candidate_indexes[offset + 1] for offset in range(len(candidate_indexes) - 1))
            )
            group_rows.append(
                {
                    "groupIndex": group["groupIndex"],
                    "wordIndexes": indexes,
                    "flaggedWordIndexes": group["flaggedWordIndexes"],
                    "sourceText": " ".join(str(word.get("text", "")) for word in source_words if int(word.get("index", -1)) in indexes),
                    "matchingWordCount": len(matched_positions),
                    "exactSequenceAgreement": exact,
                    "candidateTokenIndexes": candidate_indexes if exact else [],
                }
            )
        rows.append(
            {
                "index": position,
                "start": round(window["start"], 3),
                "end": round(window["end"], 3),
                "durationSeconds": round(window["end"] - window["start"], 3),
                "responseFile": str(response_path.relative_to(output)),
                "sourceWordIndexes": source_indexes,
                "sourceText": " ".join(str(word.get("text", "")) for word in source_words),
                "candidateText": response["text"],
                "candidateWords": candidate_words,
                "flaggedWordIndexes": sorted({index for group in window["groups"] for index in group["flaggedWordIndexes"]}),
                "comparison": {key: value for key, value in comparison.items() if key != "matches"},
                "groups": group_rows,
            }
        )
        print(
            f"Window {position + 1}/{len(windows)}: {window['end']-window['start']:.1f}s; "
            f"token matches={comparison['matchingWords']}/{comparison['sourceWords']}.",
            flush=True,
        )

    report = {
        "schemaVersion": 1,
        "provider": "OpenAI",
        "model": args.model,
        "sourceTranscript": str(transcript_path),
        "sourceAudio": str(audio_path),
        "confidenceField": args.confidence_field,
        "flagBelow": args.flag_below,
        "flaggedWordCount": len(flagged),
        "flaggedPhraseGroupCount": len(groups),
        "windowCount": len(rows),
        "uploadedAudioSeconds": round(upload_seconds, 3),
        "estimatedCostUsd": args.estimated_cost_usd,
        "authorizedCostCeilingUsd": args.max_cost_usd,
        "humanReviewCompleted": False,
        "sourceTranscriptModified": False,
        "windows": rows,
        "note": "ASR agreement is a review clue, not proof. Candidate wording is not accepted automatically.",
    }
    (output / "automated-review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Saved private review report: {output / 'automated-review.json'}; "
        f"flagged_words={len(flagged)}, uploaded_audio_seconds={upload_seconds:.1f}, "
        f"estimated_cost=${args.estimated_cost_usd:.4f}."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"Automated first pass stopped: {error}.", file=sys.stderr)
        raise SystemExit(1)
    except Exception as error:
        print(f"Automated first pass failed ({type(error).__name__}); transcript/audio details withheld.", file=sys.stderr)
        raise SystemExit(1)
