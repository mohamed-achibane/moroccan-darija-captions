#!/usr/bin/env python3
"""Create a local, human-listenable transcript and timing review page.

This helper never uploads media or changes the transcript source. It extracts
one local audio file with FFmpeg and writes an HTML review page plus a JSON
decision ledger into a separate output directory.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a private local audio review queue from a word transcript."
    )
    parser.add_argument("--transcript", required=True, type=Path, help="Transcript JSON with a top-level words array")
    parser.add_argument("--audio", required=True, type=Path, help="Source video or audio file")
    parser.add_argument("--output", required=True, type=Path, help="New directory outside the source project")
    parser.add_argument(
        "--flag-below",
        type=float,
        help="Flag words whose alignment score is below this value; does not mean they are wrong",
    )
    parser.add_argument(
        "--confidence-field",
        default="alignmentScore",
        help="Word field to use with --flag-below (default: alignmentScore)",
    )
    parser.add_argument(
        "--padding",
        type=float,
        default=1.25,
        help="Seconds of surrounding audio to play for each cue (default: 1.25)",
    )
    parser.add_argument(
        "--flag-group-overlaps",
        action="store_true",
        help="Flag adjacent phrase-group boundaries where timed words overlap",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only this tool's three named outputs if they already exist",
    )
    return parser.parse_args()


def get_groups(transcript: dict[str, Any], words: list[dict[str, Any]]) -> dict[int, list[int]]:
    groups: dict[int, list[int]] = defaultdict(list)
    for position, word in enumerate(words):
        group = word.get("phraseGroup")
        if isinstance(group, int):
            groups[group].append(position)

    source_groups = transcript.get("phraseGroups") or transcript.get("groups") or []
    for group_position, group in enumerate(source_groups):
        if not isinstance(group, dict):
            continue
        group_id = group.get("index", group_position)
        indexes = group.get("wordIndexes") or group.get("wordIndices") or group.get("word_indices")
        if not isinstance(indexes, list):
            continue
        positions = []
        for index in indexes:
            for position, word in enumerate(words):
                if word.get("index", position) == index:
                    positions.append(position)
                    break
        if positions:
            groups[group_id] = positions
    return dict(groups)


def safe_number(value: Any, label: str, word_index: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Word {word_index} has no valid {label} time") from exc
    if number != number or number in (float("inf"), float("-inf")):
        raise ValueError(f"Word {word_index} has a non-finite {label} time")
    return number


def find_flags(
    transcript: dict[str, Any],
    words: list[dict[str, Any]],
    threshold: float | None,
    score_field: str,
    group_overlaps: bool,
    duration: float | None,
) -> dict[int, list[str]]:
    reasons: dict[int, list[str]] = defaultdict(list)
    for position, word in enumerate(words):
        index = int(word.get("index", position))
        start = safe_number(word.get("start"), "start", index)
        end = safe_number(word.get("end"), "end", index)
        if start < 0 or end <= start or (duration is not None and end > duration):
            reasons[index].append("word timing is outside valid clip bounds")
    if threshold is not None:
        for position, word in enumerate(words):
            score = word.get(score_field)
            if isinstance(score, (int, float)) and score < threshold:
                index = int(word.get("index", position))
                reasons[index].append(f"{score_field} {score:.3f} is below {threshold:.3f}")

    if group_overlaps:
        groups = get_groups(transcript, words)
        ordered = sorted(groups.items())
        for (_, left_positions), (_, right_positions) in zip(ordered, ordered[1:]):
            left = words[left_positions[-1]]
            right = words[right_positions[0]]
            overlap = safe_number(left["end"], "end", int(left.get("index", 0))) - safe_number(
                right["start"], "start", int(right.get("index", 0))
            )
            if overlap > 0:
                left_index = int(left.get("index", left_positions[-1]))
                right_index = int(right.get("index", right_positions[0]))
                reason = f"phrase-group boundary overlaps by {overlap:.3f}s"
                reasons[left_index].append(reason)
                reasons[right_index].append(reason)
    return dict(reasons)


def build_word_rows(
    words: list[dict[str, Any]],
    reasons: dict[int, list[str]],
    padding: float,
    score_field: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for position, word in enumerate(words):
        index = int(word.get("index", position))
        before = [str(item.get("text", "")) for item in words[max(0, position - 3) : position]]
        after = [str(item.get("text", "")) for item in words[position + 1 : position + 4]]
        rows.append(
            {
                "position": position,
                "index": index,
                "text": str(word.get("text", "")),
                "language": str(word.get("language", "")),
                "start": safe_number(word.get("start"), "start", index),
                "end": safe_number(word.get("end"), "end", index),
                "score": word.get(score_field),
                "scoreField": score_field,
                "reasons": reasons.get(index, []),
                "before": " ".join(before),
                "after": " ".join(after),
                "phraseGroup": word.get("phraseGroup"),
                "padding": padding,
            }
        )
    return rows


def write_html(output_path: Path, transcript: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    safe_data = json.dumps(
        {
            "title": transcript.get("title", "Transcript review"),
            "duration": transcript.get("durationSeconds", transcript.get("duration")),
            "rows": rows,
        }, ensure_ascii=False
    ).replace("<", "\\u003c")
    page = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Local listening review</title>
<style>
:root{font:16px/1.45 system-ui,sans-serif;color:#202124;background:#f4f5f7}body{margin:0}
header{position:sticky;top:0;z-index:2;background:#fff;border-bottom:1px solid #d8dce2;padding:14px 20px}
h1{font-size:1.2rem;margin:0 0 6px}.hint{font-size:.9rem;color:#475569;margin:0 0 10px}
audio{width:min(900px,100%);display:block;margin:8px 0}.controls{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
main{max-width:1180px;margin:16px auto;padding:0 16px}.card{background:#fff;border:1px solid #d8dce2;border-radius:10px;padding:12px;margin:10px 0}
.rowhead{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.badge{font-size:.78rem;background:#fff1c2;padding:2px 7px;border-radius:20px}
.context{color:#475569;margin:7px 0}.focus{font-weight:700;font-size:1.1rem}.fields{display:flex;gap:10px;align-items:end;flex-wrap:wrap}
label{display:grid;gap:3px;font-size:.82rem;color:#475569}input,select,button{font:inherit;padding:6px 8px;border:1px solid #b7bec8;border-radius:6px;background:#fff;color:#202124}
input[type=text]{min-width:140px}input[type=number]{width:96px}button{cursor:pointer}button:hover{background:#eef4ff}.play{background:#eaf5ff}
.status{min-width:170px}.comment{flex:1;min-width:200px}.summary{font-weight:600}.muted{color:#64748b}
</style></head><body>
<header><h1 id="title">Local listening review</h1>
<p class="hint">Flags are review cues, not proof of an error. Uncheck “Show flagged words only” to review every word. Listen before marking a word; record wording and timing separately. This page is local, does not upload audio, and does not edit the source transcript.</p>
<audio id="audio" controls preload="metadata" src="review-audio.mp3"></audio>
<div class="controls"><button id="playRate">Playback: 1×</button><label><input id="flaggedOnly" type="checkbox" checked> Show flagged words only</label>
<span class="summary" id="summary"></span><button id="export">Export review decisions</button></div></header>
<main><div id="list"></div></main>
<script id="data" type="application/json">__DATA__</script>
<script>
const DATA=JSON.parse(document.getElementById('data').textContent), audio=document.getElementById('audio');
document.getElementById('title').textContent=DATA.title+' — listening review';
const key='moroccan-darija-listening-review:'+DATA.title+':'+DATA.duration+':'+DATA.rows.length;
const saved=JSON.parse(localStorage.getItem(key)||'{}'), state={...saved};
for(const r of DATA.rows) state[r.index] ||= {text:r.text,start:r.start,end:r.end,wordStatus:'pending',timingStatus:'pending',note:''};
let rate=1, stopAt=null;
document.getElementById('playRate').onclick=()=>{rate=rate===1?.8:1;audio.playbackRate=rate;document.getElementById('playRate').textContent='Playback: '+(rate===1?'1×':'0.8×')};
audio.addEventListener('timeupdate',()=>{if(stopAt!==null&&audio.currentTime>=stopAt){audio.pause();stopAt=null}});
function persist(){localStorage.setItem(key,JSON.stringify(state));updateSummary()}
function updateSummary(){let wordDone=0,timeDone=0,needs=0;for(const r of DATA.rows){const s=state[r.index];if(['confirmed','corrected'].includes(s.wordStatus))wordDone++;if(['confirmed','corrected'].includes(s.timingStatus))timeDone++;if(s.wordStatus==='uncertain'||s.timingStatus==='uncertain'||s.wordStatus==='pending'||s.timingStatus==='pending')needs++}document.getElementById('summary').textContent=`Wording ${wordDone}/${DATA.rows.length} · timing ${timeDone}/${DATA.rows.length} · unresolved/pending ${needs}`}
function play(r){const s=state[r.index],pad=r.padding;const start=Math.max(0,Number(s.start)-pad),end=Math.min(Number(audio.duration)||Infinity,Number(s.end)+pad);audio.currentTime=start;audio.playbackRate=rate;stopAt=end;audio.play()}
function makeField(label,kind,r,options){const wrap=document.createElement('label');wrap.textContent=label;const input=document.createElement(kind==='select'?'select':'input');if(kind==='select'){for(const value of options){const o=document.createElement('option');o.value=value;o.textContent=value;input.append(o)}input.value=state[r.index][label==='Wording review'?'wordStatus':'timingStatus'];input.onchange=()=>{state[r.index][label==='Wording review'?'wordStatus':'timingStatus']=input.value;persist()}}else{input.type=kind;input.value=state[r.index][label];if(label==='text')input.dir='auto';if(kind==='number')input.step='0.01';input.oninput=()=>{state[r.index][label]=input.value;persist()}}wrap.append(input);return wrap}
function render(){const list=document.getElementById('list');list.replaceChildren();const only=document.getElementById('flaggedOnly').checked;for(const r of DATA.rows){if(only&&!r.reasons.length)continue;const card=document.createElement('section');card.className='card';const head=document.createElement('div');head.className='rowhead';const id=document.createElement('strong');id.textContent=`#${r.index} · ${Number(r.start).toFixed(2)}–${Number(r.end).toFixed(2)}s · ${r.language||'language n/a'}`;head.append(id);if(r.score!==null&&r.score!==undefined){const score=document.createElement('span');score.className='badge';score.textContent=`${r.scoreField} ${Number(r.score).toFixed(3)}`;head.append(score)}for(const reason of r.reasons){const b=document.createElement('span');b.className='badge';b.textContent=reason;head.append(b)}const playButton=document.createElement('button');playButton.className='play';playButton.textContent='Play word with context';playButton.onclick=()=>play(r);head.append(playButton);card.append(head);const context=document.createElement('p');context.className='context';context.dir='auto';context.textContent=(r.before?r.before+' ':'')+'⟦ '+state[r.index].text+' ⟧'+(r.after?' '+r.after:'');card.append(context);const fields=document.createElement('div');fields.className='fields';fields.append(makeField('text','text',r),makeField('start','number',r),makeField('end','number',r),makeField('Wording review','select',r,['pending','confirmed','corrected','uncertain']),makeField('Timing review','select',r,['pending','confirmed','corrected','uncertain']),makeField('note','text',r));card.append(fields);list.append(card)}}
document.getElementById('flaggedOnly').onchange=render;document.getElementById('export').onclick=()=>{persist();const decisions=DATA.rows.map(r=>({index:r.index,originalText:r.text,reviewedText:state[r.index].text,originalStart:r.start,originalEnd:r.end,reviewedStart:Number(state[r.index].start),reviewedEnd:Number(state[r.index].end),wordStatus:state[r.index].wordStatus,timingStatus:state[r.index].timingStatus,note:state[r.index].note||''}));for(const d of decisions){const textChanged=d.reviewedText!==d.originalText;const timeChanged=Math.abs(d.reviewedStart-d.originalStart)>0.000001||Math.abs(d.reviewedEnd-d.originalEnd)>0.000001;if(d.wordStatus==='corrected'&&!d.reviewedText.trim()){alert(`Word ${d.index} has an empty correction.`);return}if(d.wordStatus==='corrected'&&!textChanged){alert(`Word ${d.index} is marked corrected but its text is unchanged.`);return}if(d.wordStatus==='confirmed'&&textChanged){alert(`Word ${d.index} text changed; mark it corrected or restore the original.`);return}if(d.timingStatus==='corrected'&&!timeChanged){alert(`Word ${d.index} is marked corrected but its timing is unchanged.`);return}if(d.timingStatus==='confirmed'&&timeChanged){alert(`Word ${d.index} timing changed; mark it corrected or restore the original.`);return}if(d.timingStatus==='corrected'&&(!Number.isFinite(d.reviewedStart)||!Number.isFinite(d.reviewedEnd)||d.reviewedStart<0||d.reviewedEnd<=d.reviewedStart||d.reviewedEnd>Number(DATA.duration))){alert(`Word ${d.index} has invalid corrected timing.`);return}}const complete=decisions.every(d=>['confirmed','corrected'].includes(d.wordStatus)&&['confirmed','corrected'].includes(d.timingStatus));const out={schemaVersion:1,createdAt:new Date().toISOString(),reviewerAttestation:'The reviewer marks listening decisions in this local page; the tool does not verify that audio was heard.',completed:complete,wordCount:decisions.length,wordingReviewed:decisions.filter(d=>['confirmed','corrected'].includes(d.wordStatus)).length,timingReviewed:decisions.filter(d=>['confirmed','corrected'].includes(d.timingStatus)).length,decisions};const blob=new Blob([JSON.stringify(out,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='listening-review-decisions.json';a.click();URL.revokeObjectURL(url)};
render();updateSummary();
</script></body></html>'''
    page = page.replace("__DATA__", safe_data)
    output_path.write_text(page, encoding="utf-8")


def main() -> int:
    args = parse_args()
    transcript_path = args.transcript.expanduser().resolve()
    audio_path = args.audio.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not transcript_path.is_file() or not audio_path.is_file():
        print("Transcript or audio file does not exist", file=sys.stderr)
        return 2
    try:
        transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read transcript JSON: {exc}", file=sys.stderr)
        return 2
    words = transcript.get("words")
    if not isinstance(words, list) or not words:
        print("Transcript must contain a non-empty top-level words array", file=sys.stderr)
        return 2
    if args.padding < 0:
        print("Padding must be zero or greater", file=sys.stderr)
        return 2
    output.mkdir(parents=True, exist_ok=True)
    names = ["review-audio.mp3", "review.html", "review-queue.json"]
    existing = [output / name for name in names if (output / name).exists()]
    if existing and not args.overwrite:
        print("Output files already exist; choose a new folder or pass --overwrite", file=sys.stderr)
        return 2
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("FFmpeg is required to extract local review audio", file=sys.stderr)
        return 2
    audio_output = output / "review-audio.mp3"
    command = [
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(audio_path),
        "-map",
        "0:a:0",
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "48k",
        str(audio_output),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        print("FFmpeg could not extract review audio", file=sys.stderr)
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        return 2

    duration_value = transcript.get("durationSeconds", transcript.get("duration"))
    duration = safe_number(duration_value, "duration", -1) if duration_value is not None else None
    reasons = find_flags(
        transcript,
        words,
        args.flag_below,
        args.confidence_field,
        args.flag_group_overlaps,
        duration,
    )
    rows = build_word_rows(words, reasons, args.padding, args.confidence_field)
    queue = {
        "schemaVersion": 1,
        "sourceTranscript": str(transcript_path),
        "sourceAudio": str(audio_path),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "durationSeconds": duration,
        "wordCount": len(rows),
        "flaggedWordCount": sum(bool(row["reasons"]) for row in rows),
        "flagBelow": args.flag_below,
        "confidenceField": args.confidence_field,
        "flaggedWords": [row for row in rows if row["reasons"]],
        "allWords": rows,
        "note": "Flags prioritize listening; they do not prove a word or timestamp is wrong.",
    }
    (output / "review-queue.json").write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_html(output / "review.html", transcript, rows)
    print(f"Prepared local listening review: {output / 'review.html'}")
    print(f"Words: {len(rows)}; flagged for listening: {queue['flaggedWordCount']}")
    print("No media was uploaded and the source transcript was not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
