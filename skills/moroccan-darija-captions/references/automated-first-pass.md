# Automated first pass for flagged spans

Use this optional machine-assisted pass before a person reviews low-confidence or anomalous words. It asks an independently selected ASR model to transcribe only flagged phrase windows, compares that wording with the project transcript, and can propose local timing refinements for exact agreement runs.

This pass prioritizes review; it does not certify a transcript. A second ASR model can make the same mistake, and agreement is not ground truth. Never silently replace transcript words with model suggestions. Keep the original transcript as source of truth until a qualified listener confirms wording.

## Before uploading audio

1. Read the intake record. Confirm that the user authorized the named transcription provider, private-audio upload, model, and cost ceiling. A configured API key alone is not consent.
2. Check the provider's current official documentation for a suitable independent model and current pricing. Do not claim that a model is proven accurate for Moroccan Darija without testing this audio.
3. Estimate the cost for the flagged windows and keep it within the user's stated cap. The script requires both an estimate and the cap; it stops before upload if the estimate is over the cap.
4. Save the transcript, response JSON, and audio windows outside the source project and Git. The helper reads the API key from `OPENAI_API_KEY` and never accepts or prints it.

For an authorized OpenAI pass, run:

```sh
python3 skills/moroccan-darija-captions/scripts/automated_first_pass.py \
  --transcript /path/to/project/captions/transcript.json \
  --audio /path/to/project/media/source-video.mov \
  --output /path/to/task-work/automated-first-pass \
  --model gpt-4o-transcribe \
  --flag-below 0.5 \
  --estimated-cost-usd 0.02 \
  --max-cost-usd 0.03 \
  --authorize-openai-upload yes
```

Choose the model, score threshold, estimate, and cap from the current documentation and the user's authorization. The example values are illustrative, not a recommendation or default budget. The helper extracts phrase windows with surrounding context, merges nearby windows, saves each candidate response, and writes `automated-review.json`. It does not change the transcript.

## Compare wording

Review each flagged phrase against the independent model output:

- **Exact sequence agreement:** candidate and source tokens match in order. Treat this as provisional machine agreement only.
- **Partial agreement:** some tokens match but the sequence differs. Keep both versions visible and listen to the phrase.
- **Disagreement:** the candidate differs or omits the phrase. Do not choose one by model score alone; mark wording pending for a qualified listener.

Token normalization is only for comparison. Preserve the original Darija spelling, script, punctuation, fillers, repetitions, and word order. A spelling variation may be a real dialect choice, so do not normalize it into the source transcript.

## Propose timing refinements

If an already authorized acoustic aligner is available, align only consecutive source words that match the independent transcript exactly. Keep language-specific spans separate when the aligner requires it. Use a narrow audio crop around the existing local timing so the aligner cannot jump to another occurrence elsewhere in the clip.

The bundled WhisperX helper is optional and offline-only. It requires an existing installation and cached alignment models; it does not install packages or download weights:

```sh
python3 skills/moroccan-darija-captions/scripts/propose_consensus_timings.py \
  --transcript /path/to/project/captions/transcript.json \
  --audio /path/to/project/media/source-video.mov \
  --automated-review /path/to/task-work/automated-first-pass/automated-review.json \
  --model-dir /path/to/already-cached/alignment-models \
  --output /path/to/task-work/automated-first-pass/timing-suggestions.json
```

The helper writes suggestions only. It requires an exact, complete aligner word sequence, positive times inside the local crop, a caller-selected confidence improvement, a bounded local shift, and no newly introduced neighboring-word collision before labeling a candidate. These thresholds are guardrails, not universal measures of accuracy. If a model is missing, offline loading should fail; ask before installing or downloading it.

If no local aligner is authorized or available, use provider word timestamps only when the timed ASR's exact word sequence matches the transcript. Do not transfer fuzzy or shifted Whisper-1 timestamps onto another model's words. If the provider cannot time the trusted text, leave timing pending instead of guessing.

## Finish the review

Open the model comparison alongside the local word-by-word listening page. A qualified person still needs to confirm every spoken word across the full clip, resolve disagreement spans, and check timing proposals against the sound. Apply only corrections that the listener confirms, regenerate derived captions from the transcript source of truth when authorized, and keep the transcript labeled as a machine draft until that review is complete.

Report the provider/model, number and duration of uploaded windows, estimate and cap, token-agreement counts (not as accuracy scores), proposed/applied timing counts, human-review status, and every unresolved span. Never describe this ASR comparison or an aligner run as a person listening.
