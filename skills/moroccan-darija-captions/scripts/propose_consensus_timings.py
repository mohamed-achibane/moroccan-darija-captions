#!/usr/bin/env python3
"""Propose local acoustic timing refinements for ASR-consensus word runs.

Requires an already installed WhisperX runtime and cached aligner models. Model
loading is offline-only. The script writes suggestions; it never edits a transcript.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

# Do not download a model implicitly from this helper.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Propose WhisperX timings for exact ASR-consensus runs.")
    parser.add_argument("--transcript", required=True, type=Path)
    parser.add_argument("--audio", required=True, type=Path)
    parser.add_argument("--automated-review", required=True, type=Path, help="JSON from automated_first_pass.py")
    parser.add_argument("--model-dir", required=True, type=Path, help="Already cached aligner model directory")
    parser.add_argument("--output", required=True, type=Path, help="New JSON path outside the source project")
    parser.add_argument("--minimum-run-words", type=int, default=3)
    parser.add_argument("--padding", type=float, default=0.8, help="Local audio context around original run timing")
    parser.add_argument("--minimum-score", type=float, default=0.5, help="Caller-selected score; not a universal accuracy cutoff")
    parser.add_argument("--minimum-score-improvement", type=float, default=0.1)
    parser.add_argument("--maximum-shift", type=float, default=0.5, help="Caller-selected maximum per-word change")
    parser.add_argument("--maximum-overlap", type=float, default=0.2, help="Reject newly introduced adjacent-word overlaps above this value")
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    return parser.parse_args()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = "".join(char for char in value if not unicodedata.category(char).startswith("M") and char != "ـ")
    return "".join(char for char in value if char.isalnum() or char in "'’")


def tokens(value: str) -> list[str]:
    return [match.group(0) for match in TOKEN_RE.finditer(value)]


def word_language(word: dict[str, Any]) -> str | None:
    language = word.get("language")
    if language in {"ar", "fr", "en"}:
        return language
    parts = word.get("parts") or []
    for part in parts:
        if part.get("lang") in {"ar", "fr", "en"}:
            return part["lang"]
    if any("ARABIC" in __import__("unicodedata").name(char, "") for char in str(word.get("text", ""))):
        return "ar"
    return None


def mapped_tokens(source_words: list[dict[str, Any]], candidate_words: list[str]) -> dict[int, int]:
    expected = [normalize(str(word.get("text", ""))) for word in source_words]
    actual = [normalize(word) for word in candidate_words]
    matcher = SequenceMatcher(a=expected, b=actual, autojunk=False)
    pairs: dict[int, int] = {}
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                pairs[int(source_words[i1 + offset].get("index", i1 + offset))] = j1 + offset
    return pairs


def transcript_project_root(transcript_path: Path) -> Path:
    if transcript_path.parent.name.casefold() in {"captions", "transcripts"}:
        return transcript_path.parent.parent
    return transcript_path.parent


def eligible_runs(group: dict[str, Any], pairs: dict[int, int], words_by_index: dict[int, dict[str, Any]], minimum: int) -> list[list[int]]:
    ids = [int(index) for index in group["wordIndexes"]]
    exact: list[list[int]] = []
    current: list[int] = []
    for index in ids:
        if index not in pairs:
            if current:
                exact.append(current)
                current = []
            continue
        if current and (index != current[-1] + 1 or pairs[index] != pairs[current[-1]] + 1):
            exact.append(current)
            current = []
        current.append(index)
    if current:
        exact.append(current)

    flagged = {int(index) for index in group["flaggedWordIndexes"]}
    result: list[list[int]] = []
    for run in exact:
        language_runs: list[list[int]] = []
        language_run: list[int] = []
        for index in run:
            language = word_language(words_by_index[index])
            if language_run and word_language(words_by_index[language_run[-1]]) != language:
                language_runs.append(language_run)
                language_run = []
            language_run.append(index)
        if language_run:
            language_runs.append(language_run)
        for language_run in language_runs:
            if len(language_run) >= minimum and flagged.intersection(language_run) and word_language(words_by_index[language_run[0]]):
                result.append(language_run)
    return result


def main() -> int:
    args = parse_args()
    transcript_path = args.transcript.resolve()
    audio_path = args.audio.resolve()
    review_path = args.automated_review.resolve()
    output_path = args.output.resolve()
    model_dir = args.model_dir.resolve()
    if not transcript_path.is_file() or not audio_path.is_file() or not review_path.is_file() or not model_dir.is_dir():
        print("Transcript, audio, automated review, or cached model directory is missing")
        return 2
    if output_path.exists():
        print("Output already exists; choose a new path")
        return 2
    try:
        output_path.relative_to(transcript_project_root(transcript_path))
    except ValueError:
        pass
    else:
        print("Output must be outside the source project")
        return 2
    if (
        args.padding < 0
        or args.maximum_shift < 0
        or args.maximum_overlap < 0
        or args.minimum_run_words < 1
        or not 0 <= args.minimum_score <= 1
        or not 0 <= args.minimum_score_improvement <= 1
    ):
        print("Timing, overlap, run-length, and score thresholds must be within safe non-negative ranges")
        return 2

    import torch
    import whisperx

    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    report = json.loads(review_path.read_text(encoding="utf-8"))
    words = transcript.get("words")
    if not isinstance(words, list) or not words:
        print("Transcript must contain a non-empty words array")
        return 2
    words_by_index = {int(word.get("index", position)): word for position, word in enumerate(words)}

    jobs = []
    for window in report.get("windows", []):
        candidate_words = window.get("candidateWords") or tokens(str(window.get("candidateText", "")))
        source_words = [words_by_index[index] for index in window.get("sourceWordIndexes", []) if index in words_by_index]
        pairs = mapped_tokens(source_words, candidate_words)
        for group in window.get("groups", []):
            for run in eligible_runs(group, pairs, words_by_index, args.minimum_run_words):
                language = word_language(words_by_index[run[0]])
                run_start = min(float(words_by_index[index]["start"]) for index in run)
                run_end = max(float(words_by_index[index]["end"]) for index in run)
                clip_start = max(0.0, run_start - args.padding)
                clip_end = min(float(transcript.get("durationSeconds", transcript.get("duration", run_end))), run_end + args.padding)
                jobs.append(
                    {
                        "groupIndex": int(group["groupIndex"]),
                        "language": language,
                        "wordIndexes": run,
                        "flaggedWordIndexes": sorted(set(run) & {int(i) for i in group["flaggedWordIndexes"]}),
                        "text": " ".join(str(words_by_index[index]["text"]) for index in run),
                        "clipStart": clip_start,
                        "clipEnd": clip_end,
                    }
                )
    if not jobs:
        print("No flagged run had sufficient exact ASR agreement; no aligner was loaded")
        return 0

    torch.set_num_threads(4)
    audio = whisperx.load_audio(str(audio_path))
    models = {}
    results = []
    flagged_set = {
        int(index)
        for window in report.get("windows", [])
        for group in window.get("groups", [])
        for index in group.get("flaggedWordIndexes", [])
    }
    for job_index, job in enumerate(jobs):
        language = job["language"]
        if language not in models:
            models[language] = whisperx.load_align_model(
                language_code=language,
                device=args.device,
                model_dir=str(model_dir),
            )
        model, metadata = models[language]
        clip = audio[int(job["clipStart"] * 16_000) : int(job["clipEnd"] * 16_000)]
        clip_duration = len(clip) / 16_000
        aligned = whisperx.align(
            [{"start": 0.0, "end": clip_duration, "text": job["text"]}],
            model,
            metadata,
            clip,
            args.device,
            return_char_alignments=False,
        ).get("word_segments", [])
        expected = [normalize(str(words_by_index[index]["text"])) for index in job["wordIndexes"]]
        actual = [normalize(str(item.get("word", ""))) for item in aligned]
        complete = len(expected) == len(actual) and expected == actual
        rows = []
        for position, word_index in enumerate(job["wordIndexes"]):
            old = words_by_index[word_index]
            if position >= len(aligned) or not complete:
                rows.append({"wordIndex": word_index, "status": "incomplete_alignment"})
                continue
            item = aligned[position]
            start, end = float(item.get("start", -1)), float(item.get("end", -1))
            score = float(item.get("score", 0.0))
            old_score = float(old.get("alignmentScore", 0.0))
            proposed_start = round(start + job["clipStart"], 3)
            proposed_end = round(end + job["clipStart"], 3)
            shift = max(abs(proposed_start - float(old["start"])), abs(proposed_end - float(old["end"])))
            is_flagged = word_index in flagged_set
            valid = 0 <= start < end <= clip_duration and score >= args.minimum_score and shift <= args.maximum_shift
            if is_flagged:
                valid = valid and score - old_score >= args.minimum_score_improvement
            rows.append(
                {
                    "wordIndex": word_index,
                    "text": str(old.get("text", "")),
                    "oldStart": float(old["start"]),
                    "oldEnd": float(old["end"]),
                    "oldScore": old_score,
                    "proposedStart": proposed_start,
                    "proposedEnd": proposed_end,
                    "proposedScore": round(score, 4),
                    "shiftSeconds": round(shift, 3),
                    "flagged": is_flagged,
                    "status": "candidate" if complete and valid else "needs_review",
                }
            )
        if not complete or any(row["status"] != "candidate" for row in rows):
            for row in rows:
                if row["status"] == "candidate":
                    row["status"] = "needs_review_run_incomplete"
        results.append({**job, "completeAlignment": complete, "alignedWordCount": len(aligned), "words": rows})
        print(f"Aligned run {job_index + 1}/{len(jobs)}: {len(aligned)}/{len(job['wordIndexes'])} words.", flush=True)

    # Check candidate updates against neighboring words. Reject a run if it
    # creates a start-order inversion or a new excessive overlap.
    candidate_updates = {
        row["wordIndex"]: row
        for result in results
        for row in result["words"]
        if row.get("status") == "candidate"
    }
    trial = {
        index: {"start": float(word["start"]), "end": float(word["end"])}
        for index, word in words_by_index.items()
    }
    for index, row in candidate_updates.items():
        trial[index] = {"start": row["proposedStart"], "end": row["proposedEnd"]}
    rejected = set()
    ordered_indexes = sorted(trial)
    for previous, following in zip(ordered_indexes, ordered_indexes[1:]):
        before_a, before_b = words_by_index[previous], words_by_index[following]
        after_a, after_b = trial[previous], trial[following]
        old_overlap = float(before_a["end"]) - float(before_b["start"])
        new_overlap = after_a["end"] - after_b["start"]
        inverted = after_b["start"] < after_a["start"]
        newly_excessive = new_overlap > args.maximum_overlap and new_overlap > old_overlap + 0.001
        if inverted or newly_excessive:
            rejected.update(index for index in (previous, following) if index in candidate_updates)
    for result in results:
        for row in result["words"]:
            if row.get("wordIndex") in rejected:
                row["status"] = "needs_review_boundary_conflict"

    output = {
        "schemaVersion": 1,
        "method": "Exact ASR token agreement plus offline local WhisperX forced alignment",
        "humanReviewCompleted": False,
        "sourceTranscriptModified": False,
        "alignerLanguages": sorted(models),
        "minimumRunWords": args.minimum_run_words,
        "paddingSeconds": args.padding,
        "minimumScore": args.minimum_score,
        "minimumScoreImprovement": args.minimum_score_improvement,
        "maximumShiftSeconds": args.maximum_shift,
        "maximumOverlapSeconds": args.maximum_overlap,
        "timingCandidates": sum(row.get("status") == "candidate" for result in results for row in result["words"]),
        "runs": results,
        "note": "Candidate timings require listening review; alignment scores do not prove that the transcript is correct.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved timing suggestions without editing transcript: {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Consensus alignment failed ({type(error).__name__}); transcript/audio details withheld")
        raise SystemExit(1)
