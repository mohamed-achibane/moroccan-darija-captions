#!/usr/bin/env python3
"""Create a local, human-listenable transcript and timing review page.

This helper never uploads media or changes the transcript source. It extracts
one local audio file with FFmpeg and writes an HTML review page plus a JSON
decision ledger into a separate output directory.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
import unicodedata


TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)


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
        "--flag-alignment-seams",
        action="store_true",
        help="Flag adjacent words timed by alignment windows that meet at a chunk seam",
    )
    parser.add_argument(
        "--alignment-seam-radius",
        type=float,
        default=0.75,
        help="Flag words within this many seconds of an alignment seam (default: 0.75)",
    )
    parser.add_argument(
        "--automated-review",
        type=Path,
        help="Private automated_first_pass.py report; mismatched phrase groups are promoted for listening",
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


def normalize_token(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = "".join(char for char in value if not unicodedata.category(char).startswith("M") and char != "ـ")
    return "".join(char for char in value if char.isalnum() or char in "'’")


def promote_phrase_group_flags(
    reasons: dict[int, list[str]], words: list[dict[str, Any]], groups: dict[int, list[int]]
) -> None:
    """Make a phrase the review unit when any word in it needs attention."""
    for group_id, positions in groups.items():
        indexes = [int(words[position].get("index", position)) for position in positions]
        flagged = [index for index in indexes if reasons.get(index)]
        if not flagged:
            continue
        reason = f"phrase group {group_id} includes flagged word(s): " + ", ".join(f"#{index}" for index in flagged)
        for index in indexes:
            if index not in flagged:
                reasons.setdefault(index, []).append(reason)


def make_phrase_asr_evidence(
    words: list[dict[str, Any]], groups: dict[int, list[int]], report: dict[str, Any]
) -> dict[int, list[dict[str, Any]]]:
    """Compare complete source phrase groups with independent ASR text in each window."""
    by_index = {int(word.get("index", position)): word for position, word in enumerate(words)}
    evidence: dict[int, list[dict[str, Any]]] = defaultdict(list)
    windows = report.get("windows")
    if not isinstance(windows, list):
        raise ValueError("Automated review report must contain a windows array")

    for window in windows:
        if not isinstance(window, dict):
            continue
        source_indexes = window.get("sourceWordIndexes")
        candidate_words = window.get("candidateWords")
        if not isinstance(source_indexes, list):
            continue
        if not isinstance(candidate_words, list):
            candidate_text = window.get("candidateText")
            candidate_words = [match.group(0) for match in TOKEN_RE.finditer(candidate_text)] if isinstance(candidate_text, str) else []
        try:
            source_indexes = [int(index) for index in source_indexes]
        except (TypeError, ValueError):
            continue
        if len(set(source_indexes)) != len(source_indexes) or any(index not in by_index for index in source_indexes):
            continue
        source_words = [by_index[index] for index in source_indexes]
        source_tokens = [normalize_token(str(word.get("text", ""))) for word in source_words]
        candidate_tokens = [normalize_token(str(token)) for token in candidate_words]
        matcher = SequenceMatcher(a=source_tokens, b=candidate_tokens, autojunk=False)
        opcodes = matcher.get_opcodes()
        matched = {
            source_position: candidate_position
            for tag, i1, i2, j1, j2 in opcodes
            if tag == "equal"
            for source_position, candidate_position in zip(range(i1, i2), range(j1, j2))
        }
        source_position_by_index = {index: position for position, index in enumerate(source_indexes)}
        explicit_groups = {
            int(item["groupIndex"]): item
            for item in window.get("groups", [])
            if isinstance(item, dict) and isinstance(item.get("groupIndex"), int)
        }
        group_ids = sorted(groups)
        directly_compared = set(explicit_groups)
        flagged_indexes = window.get("flaggedWordIndexes", [])
        if isinstance(flagged_indexes, list):
            flagged_indexes = {int(index) for index in flagged_indexes if str(index).lstrip("-").isdigit()}
            directly_compared.update(
                group_id
                for group_id, positions in groups.items()
                if flagged_indexes.intersection(int(words[position].get("index", position)) for position in positions)
            )
        disputed_direct = {
            group_id
            for group_id, item in explicit_groups.items()
            if item.get("exactSequenceAgreement") is False
        }
        review_group_ids = set(directly_compared)
        for group_id in disputed_direct:
            try:
                group_position = group_ids.index(group_id)
            except ValueError:
                continue
            review_group_ids.update(group_ids[max(0, group_position - 1) : group_position + 2])

        for group_id, positions in groups.items():
            if group_id not in review_group_ids:
                continue
            indexes = [int(words[position].get("index", position)) for position in positions]
            if not indexes or not set(indexes).issubset(source_position_by_index):
                continue  # Do not compare partial phrase groups at a window edge.
            local_positions = [source_position_by_index[index] for index in indexes]
            start_position, end_position = min(local_positions), max(local_positions) + 1
            group_matches = [position for position in local_positions if position in matched]
            candidate_positions = [matched[position] for position in group_matches]
            exact = (
                len(group_matches) == len(local_positions)
                and candidate_positions
                == list(range(candidate_positions[0], candidate_positions[0] + len(local_positions)))
            ) if candidate_positions else False
            supplied = explicit_groups.get(group_id)
            if supplied is not None and isinstance(supplied.get("exactSequenceAgreement"), bool):
                exact = supplied["exactSequenceAgreement"]
            if exact:
                continue

            candidate_ranges: list[tuple[int, int]] = []
            for tag, i1, i2, j1, j2 in opcodes:
                overlap_start, overlap_end = max(i1, start_position), min(i2, end_position)
                if tag == "equal" and overlap_start < overlap_end:
                    candidate_ranges.append((j1 + overlap_start - i1, j1 + overlap_end - i1))
                elif tag == "replace" and overlap_start < overlap_end:
                    candidate_ranges.append((j1, j2))
                elif tag == "insert" and start_position <= i1 <= end_position:
                    candidate_ranges.append((j1, j2))
            if candidate_positions:
                left = max(0, min(candidate_positions) - 2)
                right = min(len(candidate_words), max(candidate_positions) + 3)
                candidate_positions_for_group = list(range(left, right))
            else:
                candidate_positions_for_group = sorted(
                    {
                        position
                        for left, right in candidate_ranges
                        for position in range(max(0, left), min(len(candidate_words), right))
                    }
                )
            candidate_phrase = " ".join(str(candidate_words[position]) for position in candidate_positions_for_group)
            explicit_match_count = supplied.get("matchingWordCount") if supplied is not None else None
            match_count = int(explicit_match_count) if isinstance(explicit_match_count, int) else len(group_matches)
            evidence[group_id].append(
                {
                    "provider": report.get("provider", "independent ASR"),
                    "model": report.get("model", "unknown"),
                    "windowIndex": window.get("index"),
                    "windowStart": window.get("start"),
                    "windowEnd": window.get("end"),
                    "sourceText": " ".join(str(by_index[index].get("text", "")) for index in indexes),
                    "candidatePhraseText": candidate_phrase,
                    "candidateWindowText": str(window.get("candidateText", "")),
                    "exactSequenceAgreement": False,
                    "matchingWordCount": match_count,
                    "sourceWordCount": len(indexes),
                    "note": "Machine comparison only; candidate wording is not accepted automatically.",
                }
            )
    return dict(evidence)


def find_flags(
    transcript: dict[str, Any],
    words: list[dict[str, Any]],
    threshold: float | None,
    score_field: str,
    group_overlaps: bool,
    flag_alignment_seams: bool,
    seam_radius: float,
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
    if flag_alignment_seams:
        for position, (left, right) in enumerate(zip(words, words[1:])):
            left_window, right_window = left.get("alignmentWindow"), right.get("alignmentWindow")
            if not (
                isinstance(left_window, list)
                and len(left_window) == 2
                and isinstance(right_window, list)
                and len(right_window) == 2
            ):
                continue
            try:
                left_seam, right_seam = float(left_window[1]), float(right_window[0])
            except (TypeError, ValueError):
                continue
            if left_window == right_window or abs(left_seam - right_seam) > 0.05:
                continue
            seam = (left_seam + right_seam) / 2
            left_index = int(left.get("index", position))
            right_index = int(right.get("index", position + 1))
            if abs(safe_number(left.get("end"), "end", left_index) - seam) <= seam_radius or abs(
                safe_number(right.get("start"), "start", right_index) - seam
            ) <= seam_radius:
                reason = f"word is adjacent to an alignment-window seam at {seam:.3f}s"
                reasons[left_index].append(reason)
                reasons[right_index].append(reason)
    return dict(reasons)


def build_word_rows(
    words: list[dict[str, Any]],
    reasons: dict[int, list[str]],
    padding: float,
    score_field: str,
    phrase_reviews: dict[int, dict[str, Any]],
    groups: dict[int, list[int]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    group_by_position = {
        position: group_id
        for group_id, positions in groups.items()
        for position in positions
    }
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
                "phraseGroup": word.get("phraseGroup", group_by_position.get(position)),
                "phraseReview": phrase_reviews.get(word.get("phraseGroup", group_by_position.get(position))),
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
.group-evidence{scroll-margin-top:330px;background:#fff;border:2px solid #eab308;border-radius:10px;padding:12px;margin:12px 0}.group-evidence h2{font-size:1rem;margin:0 0 6px}.group-evidence p{margin:5px 0;white-space:pre-wrap}.machine{color:#7c2d12}
</style></head><body>
<header><h1 id="title">Local listening review</h1>
<p class="hint">Flags are review cues, not proof of an error. A flagged phrase shows every word in its natural group. ASR suggestions are unverified. Uncheck “Show flagged words only” to review every word. Listen before marking wording and timing separately. This page is local, does not upload audio, and does not edit the source transcript.</p>
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
function render(){const list=document.getElementById('list');list.replaceChildren();const only=document.getElementById('flaggedOnly').checked,shownGroups=new Set();for(const r of DATA.rows){if(only&&!r.reasons.length)continue;if(r.phraseReview&&!shownGroups.has(r.phraseGroup)){shownGroups.add(r.phraseGroup);const evidence=document.createElement('section');evidence.className='group-evidence';evidence.id='group-'+r.phraseGroup;const title=document.createElement('h2');title.textContent=`Phrase group ${r.phraseGroup} · ${r.phraseReview.wordCount} words · ${Number(r.phraseReview.start).toFixed(2)}–${Number(r.phraseReview.end).toFixed(2)}s`;evidence.append(title);const source=document.createElement('p');source.dir='auto';source.textContent='Source transcript: '+r.phraseReview.sourceText;evidence.append(source);for(const item of r.phraseReview.asrEvidence||[]){const candidate=document.createElement('p');candidate.className='machine';candidate.dir='auto';candidate.textContent=`${item.provider} ${item.model} candidate (machine output, not verified): ${item.candidatePhraseText||item.candidateWindowText||'no localized candidate text'} · matched ${item.matchingWordCount}/${item.sourceWordCount} source words`;evidence.append(candidate)}list.append(evidence)}const card=document.createElement('section');card.className='card';card.id='word-'+r.index;const head=document.createElement('div');head.className='rowhead';const id=document.createElement('strong');id.textContent=`#${r.index} · ${Number(r.start).toFixed(2)}–${Number(r.end).toFixed(2)}s · ${r.language||'language n/a'}`;head.append(id);if(r.score!==null&&r.score!==undefined){const score=document.createElement('span');score.className='badge';score.textContent=`${r.scoreField} ${Number(r.score).toFixed(3)}`;head.append(score)}for(const reason of r.reasons){const b=document.createElement('span');b.className='badge';b.textContent=reason;head.append(b)}const playButton=document.createElement('button');playButton.className='play';playButton.textContent='Play word with context';playButton.onclick=()=>play(r);head.append(playButton);card.append(head);const context=document.createElement('p');context.className='context';context.dir='auto';context.textContent=(r.before?r.before+' ':'')+'⟦ '+state[r.index].text+' ⟧'+(r.after?' '+r.after:'');card.append(context);const fields=document.createElement('div');fields.className='fields';fields.append(makeField('text','text',r),makeField('start','number',r),makeField('end','number',r),makeField('Wording review','select',r,['pending','confirmed','corrected','uncertain']),makeField('Timing review','select',r,['pending','confirmed','corrected','uncertain']),makeField('note','text',r));card.append(fields);list.append(card)}}
function focusReviewAt(){const requested=Number(new URLSearchParams(location.search).get('at'));if(!Number.isFinite(requested))return;const row=DATA.rows.find(item=>item.reasons.length&&item.end>=requested);if(!row)return;(document.getElementById('group-'+row.phraseGroup)||document.getElementById('word-'+row.index))?.scrollIntoView({block:'start'});const seek=()=>{audio.currentTime=Math.max(0,requested-1)};if(audio.readyState>=1)seek();else audio.addEventListener('loadedmetadata',seek,{once:true})}
document.getElementById('flaggedOnly').onchange=render;document.getElementById('export').onclick=()=>{persist();const decisions=DATA.rows.map(r=>({index:r.index,originalText:r.text,reviewedText:state[r.index].text,originalStart:r.start,originalEnd:r.end,reviewedStart:Number(state[r.index].start),reviewedEnd:Number(state[r.index].end),wordStatus:state[r.index].wordStatus,timingStatus:state[r.index].timingStatus,note:state[r.index].note||''}));for(const d of decisions){const textChanged=d.reviewedText!==d.originalText;const timeChanged=Math.abs(d.reviewedStart-d.originalStart)>0.000001||Math.abs(d.reviewedEnd-d.originalEnd)>0.000001;if(d.wordStatus==='corrected'&&!d.reviewedText.trim()){alert(`Word ${d.index} has an empty correction.`);return}if(d.wordStatus==='corrected'&&!textChanged){alert(`Word ${d.index} is marked corrected but its text is unchanged.`);return}if(d.wordStatus==='confirmed'&&textChanged){alert(`Word ${d.index} text changed; mark it corrected or restore the original.`);return}if(d.timingStatus==='corrected'&&!timeChanged){alert(`Word ${d.index} is marked corrected but its timing is unchanged.`);return}if(d.timingStatus==='confirmed'&&timeChanged){alert(`Word ${d.index} timing changed; mark it corrected or restore the original.`);return}if(d.timingStatus==='corrected'&&(!Number.isFinite(d.reviewedStart)||!Number.isFinite(d.reviewedEnd)||d.reviewedStart<0||d.reviewedEnd<=d.reviewedStart||d.reviewedEnd>Number(DATA.duration))){alert(`Word ${d.index} has invalid corrected timing.`);return}}const complete=decisions.every(d=>['confirmed','corrected'].includes(d.wordStatus)&&['confirmed','corrected'].includes(d.timingStatus));const out={schemaVersion:1,createdAt:new Date().toISOString(),reviewerAttestation:'The reviewer marks listening decisions in this local page; the tool does not verify that audio was heard.',completed:complete,wordCount:decisions.length,wordingReviewed:decisions.filter(d=>['confirmed','corrected'].includes(d.wordStatus)).length,timingReviewed:decisions.filter(d=>['confirmed','corrected'].includes(d.timingStatus)).length,decisions};const blob=new Blob([JSON.stringify(out,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='listening-review-decisions.json';a.click();URL.revokeObjectURL(url)};
render();updateSummary();focusReviewAt();
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
    if args.padding < 0 or args.alignment_seam_radius < 0:
        print("Padding and alignment seam radius must be zero or greater", file=sys.stderr)
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
    groups = get_groups(transcript, words)
    reasons = find_flags(
        transcript,
        words,
        args.flag_below,
        args.confidence_field,
        args.flag_group_overlaps,
        args.flag_alignment_seams,
        args.alignment_seam_radius,
        duration,
    )
    promote_phrase_group_flags(reasons, words, groups)
    asr_report: dict[str, Any] | None = None
    asr_evidence: dict[int, list[dict[str, Any]]] = {}
    if args.automated_review:
        report_path = args.automated_review.expanduser().resolve()
        try:
            asr_report = json.loads(report_path.read_text(encoding="utf-8"))
            asr_evidence = make_phrase_asr_evidence(words, groups, asr_report)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"Could not read automated review report: {exc}", file=sys.stderr)
            return 2
        for group_id, items in asr_evidence.items():
            positions = groups.get(group_id, [])
            indexes = [int(words[position].get("index", position)) for position in positions]
            reason = f"independent ASR disagrees with phrase group {group_id}"
            for index in indexes:
                if reason not in reasons.get(index, []):
                    reasons.setdefault(index, []).append(reason)

    phrase_reviews: dict[int, dict[str, Any]] = {}
    for group_id, positions in groups.items():
        indexes = [int(words[position].get("index", position)) for position in positions]
        if not any(reasons.get(index) for index in indexes):
            continue
        group_words = [words[position] for position in positions]
        phrase_reviews[group_id] = {
            "wordCount": len(group_words),
            "start": min(safe_number(word.get("start"), "start", int(word.get("index", 0))) for word in group_words),
            "end": max(safe_number(word.get("end"), "end", int(word.get("index", 0))) for word in group_words),
            "sourceText": " ".join(str(word.get("text", "")) for word in group_words),
            "asrEvidence": asr_evidence.get(group_id, []),
            "reasons": sorted({reason for index in indexes for reason in reasons.get(index, [])}),
        }
    rows = build_word_rows(words, reasons, args.padding, args.confidence_field, phrase_reviews, groups)
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
        "automatedReview": (
            {
                "provider": asr_report.get("provider"),
                "model": asr_report.get("model"),
                "sourceReport": str(args.automated_review.expanduser().resolve()),
                "humanReviewCompleted": False,
            }
            if asr_report is not None
            else None
        ),
        "phraseReviewGroupCount": len(phrase_reviews),
        "phraseReviews": phrase_reviews,
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
