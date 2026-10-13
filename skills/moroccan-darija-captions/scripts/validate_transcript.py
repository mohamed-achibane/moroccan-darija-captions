#!/usr/bin/env python3
"""Read-only validation for normalized HyperFrames caption transcript JSON."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


TIME_TOLERANCE = 0.05
LANGUAGE_DIRECTIONS = {"ar": "rtl", "fr": "ltr", "en": "ltr"}


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["top level must be a JSON object"]

    duration = document.get("duration")
    if not is_number(duration) or duration <= 0:
        errors.append("duration must be a finite number greater than zero")
        duration = None

    words = document.get("words")
    groups = document.get("groups")
    if not isinstance(words, list) or not words:
        errors.append("words must be a non-empty array")
        words = []
    if not isinstance(groups, list) or not groups:
        errors.append("groups must be a non-empty array")
        groups = []

    word_by_id: dict[int, dict[str, Any]] = {}
    word_position: dict[int, int] = {}
    prior_start = -math.inf

    for position, word in enumerate(words):
        label = f"words[{position}]"
        if not isinstance(word, dict):
            errors.append(f"{label} must be an object")
            continue

        word_id = word.get("index")
        if not isinstance(word_id, int) or isinstance(word_id, bool):
            errors.append(f"{label}.index must be an integer")
        elif word_id in word_by_id:
            errors.append(f"{label}.index duplicates word index {word_id}")
        else:
            word_by_id[word_id] = word
            word_position[word_id] = position

        start, end = word.get("start"), word.get("end")
        times_valid = is_number(start) and is_number(end)
        if not times_valid:
            errors.append(f"{label} start and end must be finite numbers")
        else:
            if start < 0 or end <= start:
                errors.append(f"{label} must have 0 <= start < end")
            if duration is not None and end > duration + TIME_TOLERANCE:
                errors.append(f"{label}.end exceeds clip duration")
            if start < prior_start:
                errors.append(f"{label}.start is out of transcript order")
            prior_start = start

        if not isinstance(word.get("text"), str) or not word["text"].strip():
            errors.append(f"{label}.text must be a non-empty string")

        parts = word.get("parts")
        if not isinstance(parts, list) or not parts:
            errors.append(f"{label}.parts must be a non-empty array")
            continue
        for part_position, part in enumerate(parts):
            part_label = f"{label}.parts[{part_position}]"
            if not isinstance(part, dict):
                errors.append(f"{part_label} must be an object")
                continue
            if not isinstance(part.get("text"), str) or not part["text"].strip():
                errors.append(f"{part_label}.text must be a non-empty string")
            lang = part.get("lang")
            if lang not in LANGUAGE_DIRECTIONS:
                errors.append(f"{part_label}.lang must be ar, fr, or en")
                continue
            expected_direction = LANGUAGE_DIRECTIONS[lang]
            if part.get("dir") != expected_direction:
                errors.append(f"{part_label}.dir must be {expected_direction} for lang={lang}")

    seen_in_groups: dict[int, int] = {}
    prior_group_start = -math.inf
    for position, group in enumerate(groups):
        label = f"groups[{position}]"
        if not isinstance(group, dict):
            errors.append(f"{label} must be an object")
            continue
        indices = group.get("wordIndices")
        if not isinstance(indices, list) or not indices:
            errors.append(f"{label}.wordIndices must be a non-empty array")
            continue

        resolved_positions: list[int] = []
        for word_id in indices:
            if not isinstance(word_id, int) or isinstance(word_id, bool) or word_id not in word_by_id:
                errors.append(f"{label} references unknown word index {word_id!r}")
                continue
            seen_in_groups[word_id] = seen_in_groups.get(word_id, 0) + 1
            resolved_positions.append(word_position[word_id])

        if resolved_positions:
            if resolved_positions != sorted(resolved_positions):
                errors.append(f"{label} wordIndices are not in transcript order")
            if any(right != left + 1 for left, right in zip(resolved_positions, resolved_positions[1:])):
                errors.append(f"{label} wordIndices must form one consecutive phrase")

        start, end = group.get("start"), group.get("end")
        if not is_number(start) or not is_number(end):
            errors.append(f"{label} start and end must be finite numbers")
            continue
        if start < 0 or end <= start:
            errors.append(f"{label} must have 0 <= start < end")
        if duration is not None and end > duration + TIME_TOLERANCE:
            errors.append(f"{label}.end exceeds clip duration")
        if start < prior_group_start:
            errors.append(f"{label}.start is out of group order")
        prior_group_start = start

        valid_group_words = [word_by_id[i] for i in indices if isinstance(i, int) and i in word_by_id]
        if valid_group_words and all(is_number(w.get("start")) and is_number(w.get("end")) for w in valid_group_words):
            first_start = min(w["start"] for w in valid_group_words)
            last_end = max(w["end"] for w in valid_group_words)
            if start > first_start + TIME_TOLERANCE:
                errors.append(f"{label}.start begins after its first word")
            if end + TIME_TOLERANCE < last_end:
                errors.append(f"{label}.end ends before its last word")

    for word_id in word_by_id:
        count = seen_in_groups.get(word_id, 0)
        if count == 0:
            errors.append(f"word index {word_id} is not included in any group")
        elif count > 1:
            errors.append(f"word index {word_id} appears in {count} groups")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path, help="normalized transcript JSON to inspect")
    args = parser.parse_args()

    try:
        document = json.loads(args.transcript.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"ERROR: cannot read {args.transcript}: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {args.transcript} at line {exc.lineno}, column {exc.colno}", file=sys.stderr)
        return 2

    errors = validate(document)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Found {len(errors)} transcript issue(s).")
        return 1

    print(f"Transcript structure is valid: {len(document['words'])} words, {len(document['groups'])} groups.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

