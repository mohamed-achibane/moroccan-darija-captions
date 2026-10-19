# Normalized transcript format

Use this format when a project does not already have a transcript schema. It keeps acoustic timing, visible text, language direction, and phrase grouping together without changing the spoken wording.

```json
{
  "duration": 6.4,
  "words": [
    {
      "index": 0,
      "start": 0.42,
      "end": 0.83,
      "text": "هاد",
      "parts": [{ "lang": "ar", "dir": "rtl", "text": "هاد" }]
    },
    {
      "index": 1,
      "start": 0.86,
      "end": 1.36,
      "text": "captions",
      "parts": [{ "lang": "en", "dir": "ltr", "text": "captions" }]
    }
  ],
  "groups": [
    { "start": 0.42, "end": 1.36, "wordIndices": [0, 1] }
  ]
}
```

## Rules

- `duration` is the final video duration in seconds.
- `words` contains every spoken word in audio order. `index` values are unique integers; `start` and `end` are measured from the final video clock.
- `text` preserves the reviewed source transcript spelling, case, and punctuation. Store display-only changes, such as uppercase Latin or punctuation removal, in the renderer instead.
- `parts` separates script runs inside a word when needed. Use `ar` with `rtl` for Arabic-script Darija/Arabic, and `fr` or `en` with `ltr` for French/English. Keep each string in its logical reading order.
- `groups` are natural phrase-sized groups. Every word belongs to exactly one group; indices in a group must be consecutive and remain in transcript order. By default, a renderer shows one timed word at a time; when the user chooses two-word display, it may show a two-word window without changing the transcript grouping. Display grouping never replaces word-level timing.
- All timestamps must satisfy `0 <= start < end <= duration` (a 50 ms end tolerance is accepted by the validator for rounding).
- These are schema rules, not a timing method. Use provider timestamps only when reliable; otherwise run acoustic alignment and review uncertain boundaries against audio.

## Structural validator

Run the bundled, dependency-free validator on a transcript file:

```sh
python3 skills/moroccan-darija-captions/scripts/validate_transcript.py transcript.json
```

It checks JSON structure, timestamp bounds and ordering, language/direction labels, and phrase-group coverage. It cannot confirm that words or timings match the audio; a person still needs to listen and review them.
