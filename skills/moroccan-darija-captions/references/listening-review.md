# Listening review

Listening review is a quality step, not a model name. Speech recognition proposes words, and forced alignment estimates where supplied words occur. Neither proves that a word was heard correctly or that its boundary matches the sound.

Before asking a person to focus on flagged spans, optionally run the separate [automated first pass](automated-first-pass.md) when its provider upload and cost were authorized. Keep its candidate wording and timing proposals clearly labeled as machine output; it does not replace listening.

## Choose the reviewer honestly

1. If the active assistant has genuine audio input and the user authorized that provider and cost, it may make a **model-assisted audio audit**. Record the model and mark the result as machine-reviewed. Do not describe that as a human listening review or as ground truth.
2. Otherwise, use a person who can understand the spoken languages. For Moroccan Darija, ask a fluent speaker to resolve uncertain wording, names, and code-switches. An assistant that cannot receive or perceive the audio must not claim it listened just because it generated a transcript, opened a player, inspected a waveform, or ran an aligner.
3. If no qualified listener is available, prepare the local review queue, leave items pending, and label the transcript as an unreviewed draft. Ask the creator to resolve the remaining words before calling the captions publishable.

## Prepare and run a local review

Use the bundled helper when Python and FFmpeg are available. Save output outside the source project and outside Git because it contains private audio and transcript text:

```sh
python3 skills/moroccan-darija-captions/scripts/prepare_listening_review.py \
  --transcript /path/to/project/captions/transcript.json \
  --audio /path/to/project/media/source-video.mov \
  --output /path/to/task-work/listening-review \
  --flag-below 0.5 \
  --flag-group-overlaps
```

The score threshold is a caller choice, not a universal accuracy cutoff. The helper writes a local MP3 audio copy, `review.html`, and `review-queue.json`. Open `review.html` in a local browser; if the browser blocks a `file://` audio source, serve that folder on loopback only and open the local URL. The page starts with flagged words but can show every word. Use **Play word with context** at normal speed first; use 0.8× only to resolve a difficult boundary. Listen to a phrase at normal speed again before confirming a correction. Use the neighboring words to preserve Darija morphology, fillers, repetitions, and language switches.

When an independent ASR comparison exists, pass it into the same queue:

```sh
python3 skills/moroccan-darija-captions/scripts/prepare_listening_review.py \
  --transcript /path/to/project/captions/transcript.json \
  --audio /path/to/project/media/source-video.mov \
  --automated-review /path/to/task-work/automated-first-pass/automated-review.json \
  --output /path/to/task-work/listening-review-with-asr \
  --flag-below 0.5 \
  --flag-group-overlaps \
  --flag-alignment-seams
```

The queue promotes every word in a phrase group when any member has a low score, invalid timing, boundary overlap, or alignment-seam cue. With an automated report, it also compares complete source phrase groups covered by each ASR window and promotes every word in a group whose sequence disagrees. The page shows the source phrase and a localized candidate excerpt with its model labelled clearly as unverified output. A neighboring agreement cannot make a disputed group safe automatically; listen to the complete group, including every word whose score sits just above the cutoff. Groups cut off by an ASR window edge are not compared as if they were complete.

For chunked alignments, use overlapping audio context between neighboring chunks when producing new timings. Compare the shared words and keep all times on the original clip clock. When only non-overlapping chunk metadata is available, `--flag-alignment-seams` promotes words near those boundaries so the listener can check for jumps or early captions. The seam radius is a review heuristic, not an accuracy threshold.

For each word, record two separate decisions:

- **Wording:** confirmed, corrected, or uncertain.
- **Timing:** confirmed, corrected, or uncertain.

Review all words in each flagged phrase group together. A phrase-level flag means “listen to this unit,” not that each word is wrong. Keep independent ASR text visible as a suggestion only. Confirm wording and timing against the audio separately; do not use the ASR candidate itself as a correction or timing anchor until the wording is trusted.

Add a short note for corrections or unresolved items. Export the decision ledger from the page. Review the ledger before applying any changes to the transcript source. Apply only confirmed corrections to the transcript and rerun alignment on corrected phrases; do not shift the full timeline to fix a local issue. Keep the audio original and read-only.

## Completion and reporting

- Wording review is complete only when every spoken word across the clip was checked against audio by a qualified person, or when the result is explicitly labeled as a model-assisted audit.
- Timing review is complete only when every word has a valid start/end and all flagged or anomalous boundaries were listened to; spot-check a sample of unflagged words and phrase boundaries too.
- Any pending or uncertain item keeps the result in draft/review status. Do not turn a structural validator, ASR confidence, aligner score, or second model's agreement into an accuracy claim.
- Report who or what reviewed the audio, full-clip versus partial coverage, the numbers confirmed/corrected/uncertain, and the remaining issues. Never say a person listened unless a person actually did.

The decision page is a local human-review aid. It does not send audio to a provider, edit the source transcript, or certify that a person listened.
