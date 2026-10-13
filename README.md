# Moroccan Darija Captions

Reusable agent skills and caption tools for vertical videos spoken in Moroccan Darija, Arabic, French, and English.

Darija stays in Arabic script. French and English stay in Latin script. The workflow reviews the transcript against the complete audio, aligns every word, then renders captions with HyperFrames or Remotion.

## Choose your setup

The assistant, transcription service, and video editor are separate choices:

| First choose | Options |
|---|---|
| Assistant ecosystem | Codex, ChatGPT app, Claude, or Gemini |
| Speech recognition | A current API model, or a local WhisperX workflow |
| Video editor | HyperFrames or Remotion |

Start with [`START-HERE.md`](START-HERE.md). If the assistant is missing this information, the router skill asks which ecosystem you use, then points to its dedicated skill. The platform skills are in [`skills/`](skills/).

## How it works

1. **Transcribe:** choose a current model that supports the languages and workflow you need. No vendor is declared the universal winner; model names, features, and prices change.
2. **Review and align:** check the full transcript against the audio. Use the provider’s word timestamps when reliable; otherwise use an acoustic aligner such as WhisperX, then inspect uncertain words and boundaries.
3. **Compose:** choose HyperFrames or Remotion. Keep the original video, audio, and opening title intact unless the user requests a different edit.
4. **Review and deliver:** review the opening, a mixed-script passage, and the ending. Provide the editable project and a fresh MP4 when requested and authorized.

WhisperX is a local Whisper-based transcription and forced-alignment workflow; it is not interchangeable with an API transcription model. A text model writes the words; an aligner estimates where those reviewed words occur in the audio.

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
| Arabic | Logical RTL order, `dir="rtl"`, `lang="ar"`; Myriad Arabic Bold, 140px base at `1.12em` (about 157px). Ask before substituting if unavailable. |
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
| `skills/moroccan-darija-captions/references/transcript-schema.md` | Normalized word and phrase-group data format. |
| `skills/moroccan-darija-captions/scripts/validate_transcript.py` | Read-only structural validation for normalized transcript JSON. |
| `docs/INSTALL.md` | Installation and capability notes for each ecosystem. |

## Safety and quality

- Keep source video files untouched and work in a separate project folder.
- Use only credentials the user has authorized. Keep keys in the provider’s supported secret store or environment, never in prompts, transcripts, source control, or logs.
- A model’s language list does not prove its accuracy on Moroccan Darija or code-switching. Review a representative sample and then the complete transcript.
- Do not invent word timings. If an aligner cannot place a word reliably, mark it for review.
- Respect the current project’s checks, build, browser, and render authorization rules. Never commit or push rendered video unless specifically requested for that video.

## License and credit

MIT. See [`LICENSE`](LICENSE). The workflow was informed by the public [Darija word captions project](https://github.com/benmouad-ai/darija-word-captions); see [`CREDITS.md`](CREDITS.md).
