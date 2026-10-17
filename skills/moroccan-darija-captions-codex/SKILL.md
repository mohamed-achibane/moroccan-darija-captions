---
name: moroccan-darija-captions-codex
description: Use the Moroccan Darija captions workflow from Codex for a local video project, including reviewed mixed-script transcription, word alignment, HyperFrames or Remotion editing, and safe delivery.
---

# Moroccan Darija Captions for Codex

This is the Codex entry skill. Read the shared workflow at `../moroccan-darija-captions/SKILL.md` and its Codex adapter at `../moroccan-darija-captions/references/platforms/codex.md`, then follow them for the whole task.

This entry skill establishes Codex as the assistant ecosystem. Do not ask the user which ecosystem they use. Before asking about transcription, alignment, editor, or delivery, follow the shared [one-time intake](../moroccan-darija-captions/references/intake.md): perform scoped read-only discovery of local models, relevant provider credential availability, and the tools this Codex environment can actually use; then ask all unanswered questions together.

Use the project’s available Codex tools for local files, commands, and Studio preview. Treat explicit intake consent as covering the named checks, build, preview, and render for this video; do not ask again for those same actions. Pause if later work would exceed the named provider, cost, upload, or installation scope. Never inspect or display credential values, and never replace or overwrite the user’s existing local skill when installing this public version.

For audio review, follow the shared [`listening-review.md`](../moroccan-darija-captions/references/listening-review.md). Codex may prepare the local review page with `prepare_listening_review.py`, but opening or generating that page does not mean the agent heard the audio. If the active Codex model/tool surface cannot receive audio, keep the review pending for a qualified human listener and report that limitation accurately.

Before human review of flagged spans, follow the shared [`automated-first-pass.md`](../moroccan-darija-captions/references/automated-first-pass.md) when the user authorized an independent ASR provider and cost. Use `automated_first_pass.py` for an OpenAI comparison and `propose_consensus_timings.py` only when WhisperX and the required models are already installed and authorized. Keep model candidates and timing proposals separate from the transcript source of truth until a person confirms them.

Merge any authorized automated comparison into `prepare_listening_review.py` with `--automated-review`. The local queue must promote every word in a phrase group when any word is low-confidence, anomalous, near a known alignment seam, or disputed by the independent recognizer. Keep the full group visible with the alternate wording clearly marked as an unverified model suggestion. Do not claim audio review or apply a wording/timing correction without evidence from the audio.
