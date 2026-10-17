# Moroccan Darija Captions

Reusable agent skills and caption tools for vertical videos spoken in Moroccan Darija, Arabic, French, and English.

Darija stays in Arabic script. French and English stay in Latin script. The workflow reviews the transcript against the complete audio, aligns every word, then renders captions with HyperFrames or Remotion.

## Creator

Created with love by **Mohamed Achibane**. These are the creator’s official profiles:

- [LinkedIn](https://www.linkedin.com/in/mohamed-achibane/)
- [Instagram](https://www.instagram.com/mohamedwebmaster/)
- [Facebook](https://www.facebook.com/MohamedWebMaster/)
- [TikTok](https://www.tiktok.com/@mohamedwebmaster)
- [YouTube](https://www.youtube.com/@mohamed.achibane)

## Choose your setup

The assistant, transcription service, and video editor are separate choices. The active entry skill identifies the assistant ecosystem; it does not select the transcription provider:

| First choose | Options |
|---|---|
| Assistant ecosystem | Codex, ChatGPT app, Claude, or Gemini |
| Speech recognition | A current API model, an already-installed local model, or an optional local model installation after a hardware check |
| Video editor | HyperFrames or Remotion |

Start with [`START-HERE.md`](START-HERE.md). The matching entry skill performs a scoped, read-only inventory before asking one consolidated intake about missing route, consent, and delivery choices. The platform skills are in [`skills/`](skills/).

## How it works

1. **Discover and choose:** inspect available local ASR/alignment tools and safe provider-credential availability, then recommend a current route for the clip. Ask once about cloud audio upload and a cost cap, local model installs/downloads, editor/output, and permission to complete the requested checks, preview, build, and render. A key's presence alone does not authorize its use.
2. **Transcribe:** use the selected current API model or local model that fits the user's computer. No vendor is declared the universal winner; model names, features, and prices change.
3. **Review and align:** optionally compare flagged spans with an independent ASR pass using [`automated-first-pass.md`](skills/moroccan-darija-captions/references/automated-first-pass.md). Merge disagreements into the listening queue at the complete phrase-group level, keep candidate wording separate from the transcript, and propose timing changes only for trusted wording. Check alignment chunk seams and use overlapping context when creating chunked timings. Then check the full transcript against the audio using the local workflow in [`listening-review.md`](skills/moroccan-darija-captions/references/listening-review.md). A model or aligner is never reported as a human listener.
4. **Compose:** use the selected HyperFrames or Remotion project. Keep the original video, audio, and opening title intact unless the user requests a different edit.
5. **Review and deliver:** review the opening, a mixed-script passage, and the ending. Provide the editable project and a fresh MP4 when requested or authorized in the one-time intake.

Local candidates include Darija-focused MoulSot and multilingual Whisper models through runtimes such as faster-whisper; WhisperX can transcribe locally and align a reviewed transcript. Local inference does not mean local installation is automatic: the skill checks compatibility and asks before installing packages or downloading weights. A text model writes the words; an aligner estimates where those reviewed words occur in the audio.

## Copyable request for your AI coder

Replace every bracketed value with your actual details before sending this prompt. Keep the explicit yes/no choices for uploads, spending, installs, checks, builds, and renders.

```text
Use the Moroccan Darija Captions skill installed for this AI environment, including its matching platform instructions. Detect which tools and permissions are actually available here; do not assume that I have a particular provider, API, editor, or renderer.

Video: [full path to the video file, or attach it]
Output folder: [full path where the editable project and authorized MP4 should go]
Editor: [HyperFrames / Remotion / recommend after inspecting what is available]
Spoken languages: [for example, Moroccan Darija in Arabic script, French and English in Latin script]
Caption style: [use the skill's 140px Arabic preset / describe my custom style]
Transcription preference: [provider and model / local model / recommend after discovery]

Before editing, inspect the computer and project read-only for existing speech models, alignment tools, provider credential availability, fonts, editor, and renderer. Never reveal or ask me to paste an API key. Recommend a transcription and word-alignment route using current official provider documentation and what is already installed. Ask me once, in one message, only for choices that are still missing.

My permissions for this video:
- Upload audio to [provider, or “no cloud upload”]: [yes/no]. Maximum transcription or alignment spend: [currency and amount, or zero].
- Install packages or download named local models: [yes/no; if yes, list what I approve and any storage limit].
- Create the editable project and open a local preview: [yes/no].
- Run project checks: [yes/no]. Build the project: [yes/no]. Render a fresh MP4: [yes/no].
- If words remain uncertain after review: [pause and ask me / leave them flagged in an unapproved review draft].

If authorized, complete the video end to end: transcribe the full audio verbatim, review the wording against the audio, align every word acoustically, compose the captions, inspect the preview, run only the checks/build/render steps I authorized, and deliver the editable project plus a fresh MP4 when rendering is authorized. Preserve the source video, audio, framing, and opening title. Keep Darija in Arabic script and spoken French/English in Latin script. Never invent wording or timings. Keep model suggestions separate from the transcript, and do not call model output a human listening review. Keep generated video files out of Git unless I explicitly ask you to commit or push this video.
```

## Install

### Codex or Claude Code

The skills follow the open `SKILL.md` format. Install the router and the matching platform skill from this repository with a skills installer, or copy both folders from `skills/` into the platform’s skill directory. Read [`docs/INSTALL.md`](docs/INSTALL.md) for platform-specific instructions.

### Gemini CLI

Gemini CLI supports agent skills. Install the repository or copy the router plus Gemini skill as described in [`docs/INSTALL.md`](docs/INSTALL.md).

### ChatGPT app

ChatGPT has a separate plugin package format for skills. This repository includes a portable [`plugin.json`](plugin.json) for Codex and ChatGPT plugin workflows. Downloading the GitHub repository alone does not install it in ChatGPT; see the guide for installation and public plugin submission.

## Caption style

The built-in style starts from the approved treatment used for this skill’s original edit. It is a starting preset, not a requirement for other creators:

| Element | Starting preset |
|---|---|
| Canvas and source | 1080×1920 portrait; preserve source footage, audio, framing, and opening title. |
| Captions | Full-clip, reviewed word timings; two consecutive words visible; highlight only the currently spoken word. |
| Arabic | Logical RTL order, `dir="rtl"`, `lang="ar"`; Myriad Arabic Bold at 140px. Ask before substituting if unavailable. |
| Latin | Dedicated row separate from Arabic; uppercase in display; Arial Bold at 100px. Preserve original transcript spelling and case. |
| Color and placement | Active `#9DDBF5`, other text `#FFF9F0`; centered in lower safe area, about 300px above bottom, with the same baseline from the opening onward. |
| Motion and decoration | Restrained fade/lift and subtle shadow; no background plate, frame, icons, or decorative graphics. |

Users can choose a different font, size, position, grouping, or color. The skill asks before making a material design choice when the user has not supplied one.

## What’s inside

| Path | Purpose |
|---|---|
| `skills/moroccan-darija-captions/` | Ecosystem chooser and shared end-to-end workflow. |
| `skills/moroccan-darija-captions-codex/` | Codex-specific entry skill. |
| `skills/moroccan-darija-captions-chatgpt/` | ChatGPT app and plugin-specific entry skill. |
| `skills/moroccan-darija-captions-claude/` | Claude-specific entry skill. |
| `skills/moroccan-darija-captions-gemini/` | Gemini-specific entry skill. |
| `skills/moroccan-darija-captions/references/transcription-models.md` | Model selection, timing, and current-doc checks. |
| `skills/moroccan-darija-captions/references/intake.md` | Discovery-first, ecosystem-aware one-time questions and consent scope. |
| `skills/moroccan-darija-captions/references/listening-review.md` | Honest, human-led listening review, model-review labeling, and completion rules. |
| `skills/moroccan-darija-captions/references/transcript-schema.md` | Normalized word and phrase-group data format. |
| `skills/moroccan-darija-captions/scripts/validate_transcript.py` | Read-only structural validation for normalized transcript JSON. |
| `skills/moroccan-darija-captions/scripts/prepare_listening_review.py` | Builds a local phrase-aware review page, merging score, timing, seam, and optional independent-ASR disagreement cues. |
| `skills/moroccan-darija-captions/scripts/automated_first_pass.py` | Sends only authorized, flagged audio windows to OpenAI and records alternative wording without editing the transcript. |
| `skills/moroccan-darija-captions/scripts/propose_consensus_timings.py` | Uses already-cached WhisperX models offline to suggest timings for exact ASR-consensus runs. |
| `skills/moroccan-darija-captions/references/automated-first-pass.md` | Consent, model comparison, conservative timing proposal, and honest-reporting workflow. |
| `docs/INSTALL.md` | Installation and capability notes for each ecosystem. |

## Safety and quality

- Keep source video files untouched and work in a separate project folder.
- Use only credentials the user has authorized. Keep keys in the provider’s supported secret store or environment, never in prompts, transcripts, source control, or logs.
- A model’s language list does not prove its accuracy on Moroccan Darija or code-switching. Review the complete transcript and keep human listening distinct from model-assisted audits.
- `skills/moroccan-darija-captions/scripts/prepare_listening_review.py` makes a local word-by-word review page and separate decision ledger. It requires Python and FFmpeg, makes no API calls, and never edits the source transcript.
- Any flagged word promotes its complete natural phrase group; an independent-ASR mismatch promotes the complete group even if some word scores are above the selected cutoff. These are listening priorities, never automatic transcript corrections.
- Do not invent word timings. If an aligner cannot place a word reliably, mark it for review.
- Respect the current project’s checks, build, browser, and render authorization rules. Never commit or push rendered video unless specifically requested for that video.

## License and credit

MIT. See [`LICENSE`](LICENSE). The workflow was informed by the public [Darija word captions project](https://github.com/benmouad-ai/darija-word-captions); see [`CREDITS.md`](CREDITS.md).
