# Start here

Before setting up a captioning workflow, identify three independent choices. Ask about any choice the user has not already made.

## 1. Which assistant ecosystem?

Ask:

> Which assistant are you using: Codex, the ChatGPT app, Claude, or Gemini? If you mean Gemini, are you using Gemini CLI or the Gemini app/web?

Then follow the matching entry skill:

| Answer | Skill |
|---|---|
| Codex | [`skills/moroccan-darija-captions-codex/SKILL.md`](skills/moroccan-darija-captions-codex/SKILL.md) |
| ChatGPT app | [`skills/moroccan-darija-captions-chatgpt/SKILL.md`](skills/moroccan-darija-captions-chatgpt/SKILL.md) |
| Claude | [`skills/moroccan-darija-captions-claude/SKILL.md`](skills/moroccan-darija-captions-claude/SKILL.md) |
| Gemini | [`skills/moroccan-darija-captions-gemini/SKILL.md`](skills/moroccan-darija-captions-gemini/SKILL.md) |

If the assistant or tool does not have access to local files, Python, FFmpeg, a browser, or a renderer, state that limitation and offer the parts it can complete. Do not imply that a chat-only assistant has rendered a local video.

## 2. Which transcription route?

Ask whether they prefer an API provider, a local model they already have, an optional local installation if their machine supports it, or a recommendation. For local use, check installed runtimes and hardware first; explain the model, platform fit, and storage/download needs, then get consent before installing software or model weights. If they want a recommendation, consult [`skills/moroccan-darija-captions/references/transcription-models.md`](skills/moroccan-darija-captions/references/transcription-models.md), check current official docs, and compare candidates on representative Darija and code-switched audio. Include accuracy, word timing, language fit, privacy, cost, and available credentials in the recommendation.

Do not present a permanent “best in the world” ranking. The right choice depends on the specific clip, model access, and whether transcript or word timing is more important. Ask before spending money on a model comparison.

## 3. Which editor?

Ask whether they want HyperFrames or Remotion if this is not already clear. Do not treat WhisperX as an editor: use it for local transcription/alignment, then render with the chosen video tool.

## Continue

Read [`skills/moroccan-darija-captions/SKILL.md`](skills/moroccan-darija-captions/SKILL.md) for the shared workflow. Keep the user's source media safe, review the complete transcript, and check the final rendered output only when the current task authorizes those actions.
