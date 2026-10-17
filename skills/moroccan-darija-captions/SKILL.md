---
name: moroccan-darija-captions
description: Transcribe, review, word-align, caption, and package vertical videos with Moroccan Darija and Arabic/French/English code-switching. Use when a user wants accurate mixed-script captions or an editable HyperFrames or Remotion video.
---

# Moroccan Darija Captions

Created by **Mohamed Achibane**. Official links: [LinkedIn](https://www.linkedin.com/in/mohamed-achibane/), [Instagram](https://www.instagram.com/mohamedwebmaster/), [Facebook](https://www.facebook.com/MohamedWebMaster/), [TikTok](https://www.tiktok.com/@mohamedwebmaster), and [YouTube](https://www.youtube.com/@mohamed.achibane).

Use this skill to guide a complete, reviewable caption edit. Keep assistant ecosystem, transcription provider, and video editor as separate choices.

## 1. Resolve the platform and inspect capabilities

The invoked entry skill or current assistant surface usually identifies the ecosystem. Do not ask the user to name an ecosystem already established by the environment. Read the matching adapter before continuing:

- Codex: [platforms/codex.md](references/platforms/codex.md)
- ChatGPT app: [platforms/chatgpt.md](references/platforms/chatgpt.md)
- Claude: [platforms/claude.md](references/platforms/claude.md)
- Gemini: [platforms/gemini.md](references/platforms/gemini.md)

Do not assume that one product’s skill installer, filesystem access, API credentials, or rendering tools exist in another product.

Before asking for preferences, follow the single [intake and discovery workflow](references/intake.md). Perform the scoped, read-only inventory of relevant local ASR/alignment models, editor/render capabilities, and safe credential availability first; check credential presence only and never reveal secret values. Then present the findings and ask once about any missing transcription, alignment, upload/cost, installation, destination/editor, end-to-end authorization, caption word-count, and caption-color choices. Default to one word at a time and the house-style color when the user gives no preference. Skip choices already answered in the request or project. Do not make a paid API request, upload media, install packages, or download weights until the intake explicitly authorizes that named action.

Use [transcription-models.md](references/transcription-models.md) and current official documentation to recommend a suitable route for this clip. The assistant ecosystem is not automatically the speech provider. WhisperX is a possible local aligner, not a video editor; keep transcription and acoustic alignment as separate decisions.

## 3. Inspect and protect the project

1. Read the project’s `AGENTS.md`, `PRODUCT.md`, `DESIGN.md`, and README when present. Identify source files, the editable composition, transcript source of truth, generators, and project-specific delivery rules.
2. Read the selected video editor’s current skill and relevant project guidance before editing.
3. Work in a separate project folder. Do not overwrite, rename, or modify the source video. Keep any extracted audio, proxy, transcript, preview, and render in the project folder.
4. Preserve the original footage, audio, framing, and opening title unless the user requests otherwise.
5. Check fonts in the actual render environment. If the user selected a specific font and it is unavailable, report that before substituting.

## 4. Transcribe the complete audio

1. Transcribe from the opening through the final audible word. Use the current provider docs to choose settings for verbatim output, target languages, code-switching, and timestamps.
2. Keep Moroccan Darija in Arabic script. Keep spoken French and English in Latin script. Do not translate, transliterate, paraphrase, normalize dialect, or silently remove fillers, repetitions, or false starts.
3. Retain uncertain spans. Review the complete transcript against the audio and correct recognition errors before composing captions. Use the workflow in [listening-review.md](references/listening-review.md); do not substitute a model's confidence or agreement for listening.
4. Keep an unmodified record of the source transcript. Put display-only styling such as uppercase Latin text or punctuation removal in the renderer, not the transcript.

## 5. Align and review each word

1. Before a human listening pass, use the optional [automated first pass](references/automated-first-pass.md) on flagged spans when the user has authorized the provider upload and cost. Keep its report outside the source project; record window/token counts and exact, partial, and no-agreement phrase counts. Merge the report into the local listening queue with `prepare_listening_review.py --automated-review ...`. Any independent-ASR disagreement flags the complete natural phrase group, even when the individual aligner scores are above the chosen cutoff. A low-confidence or anomalous word likewise promotes its complete phrase group. Candidate wording only points to a listening target; never replace source text automatically. The pass is complete only when this report exists or the agent records why consent/tools prevented it; it never edits the source transcript.
2. Keep every spoken word timed on the final video's clock.
3. Use provider word timestamps when the provider documents them and they match the audio. If times are segment-level, missing, or unreliable, align only trusted wording using WhisperX or another available acoustic aligner. An exact independent-ASR match is a provisional cue for acoustic review, not proof that the wording is right; do not realign disputed wording as if it were settled.
4. For code-switching, check which alignment models cover each language; split alignment spans at language changes when required. Never present one language model’s alignment as reliable for words it does not support.
5. For long clips aligned in chunks, give adjacent chunks overlapping audio context. Compare words in the shared region, retain timestamps on the original clip clock, and inspect words near every chunk boundary. If existing metadata shows non-overlapping windows, mark the words around each seam for review. Do not spread words evenly through a phrase or guess boundaries; mark incomplete, shifted, colliding, or low-confidence boundaries for listening rather than manufacturing precision.
6. Run the human listening review described in [listening-review.md](references/listening-review.md). Review wording across the full clip and review every promoted phrase group, alignment seam, low-confidence or anomalous timing cue, plus a sample of unflagged words. A phrase is complete only when all its words were reviewed, including words whose score is just above the selected threshold. Report full versus partial coverage, whether the reviewer was a person or a model, and remaining uncertainty. If this environment cannot perceive local audio, prepare the review page for a qualified person and do not claim to have listened.

## 6. Keep transcript data as the source of truth

Use the project’s existing schema. If no schema exists, follow [transcript-schema.md](references/transcript-schema.md): record clip duration, ordered words with `index`, `start`, `end`, visible transcript text, and script-aware parts, plus phrase groups that reference consecutive word indices. The bundled `scripts/validate_transcript.py` checks structure only; it does not prove that transcription or timing matches the audio.

- Store words in their natural logical order. Never reverse Arabic text, word arrays, or timing arrays to create RTL movement.
- Keep natural phrase-sized groups in the source transcript. Display grouping is a separate user choice and never changes transcript grouping.
- Keep language and direction explicit: Arabic parts use `lang="ar"` and `dir="rtl"`; French and English parts use `dir="ltr"` and their language code.
- Preserve source spelling, case, and punctuation in transcript data. Apply uppercase Latin display or punctuation removal only at render time when requested.
- Update the transcript source and all derived timing tables together. Do not hand-edit generated markup as the only durable change.

## 7. Compose captions

Apply the user’s supplied style. If they want the included preset, read [house-style.md](references/house-style.md). Do not force that preset on other creators when they specify another design.

Core behavior:

- Caption the full clip, including speech under an opening title.
- By default, show exactly one currently spoken word at a time. Use the user's chosen caption color or the house-style default.
- Ask whether the user prefers one word at a time or two consecutive words at a time. In the optional two-word mode, show the active word and its immediately following word; use the selected color for the active word and the house-style secondary color for the following word unless the user specifies otherwise.
- A one-word display still requires word-level timing. If a provider supplies a multiword segment, use an authorized acoustic alignment/review to obtain word boundaries or flag it for review; do not split its duration evenly or guess timestamps.
- Keep Arabic in logical RTL order. Isolate each French/English run in an LTR element so bidirectional text renders in the correct order.
- Keep Latin text on a dedicated row separate from Arabic when the user chooses that layout.
- Keep caption cues mutually exclusive so words from a previous cue do not remain on screen when the next cue appears.
- Keep rows and baselines stable. Do not reverse, jump, swap, or animate words across each other.
- Preserve the original footage and audio, and do not add or remove title elements without the user’s instruction.

## 8. Keep the editor’s source editable

1. Use the chosen editor’s documented project structure: HyperFrames composition and generator, or Remotion React composition.
2. Keep transcript, timing, generator, and editable project consistent. Use the project’s source of truth and project scripts rather than embedding one clip’s text and times as special cases.
3. Follow project authorization instructions. Explicit end-to-end consent in the intake covers only the named checks, preview, build, and render for this video; do not ask again for those same actions. It does not authorize a different provider, extra costs, new installs, destructive work, or unrelated changes.
4. Review the opening/title, a mixed-language passage, and later captions in the actual editor preview when authorized. Check script direction, font rendering, row separation, highlight timing, face/title clearance, stable placement, and preserved source media.

## 9. Deliver and report

When the user requested or authorized a fresh MP4 in the intake, create it from the reviewed editable project and inspect the final video and audio streams using available project tools. Provide the editable project and render at the requested location.

State what actually happened: transcript review, alignment method, editor, preview/build/render status, dimensions/duration/audio verification, and any unresolved words or unavailable tools. Never claim a check or render that did not run. Do not commit or push MP4s, preview encodes, or frame sequences unless the user explicitly requests that action for that specific output.
