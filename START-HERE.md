# Start here

Use the entry skill for the assistant environment already in use. Do not ask the user to identify an ecosystem that is clear from the active skill or environment. Ask whether they mean Gemini CLI or Gemini app/web, or Claude Code or Claude app/web, only when the current surface cannot be determined.

Follow the matching entry skill:

| Answer | Skill |
|---|---|
| Codex | [`skills/moroccan-darija-captions-codex/SKILL.md`](skills/moroccan-darija-captions-codex/SKILL.md) |
| ChatGPT app | [`skills/moroccan-darija-captions-chatgpt/SKILL.md`](skills/moroccan-darija-captions-chatgpt/SKILL.md) |
| Claude | [`skills/moroccan-darija-captions-claude/SKILL.md`](skills/moroccan-darija-captions-claude/SKILL.md) |
| Gemini | [`skills/moroccan-darija-captions-gemini/SKILL.md`](skills/moroccan-darija-captions-gemini/SKILL.md) |

If the assistant or tool does not have access to local files, Python, FFmpeg, a browser, or a renderer, state that limitation. Do not imply that a chat-only assistant has inspected the user's computer or rendered a local video.

## Start every video task with discovery

Before asking for provider or editor choices, follow [`skills/moroccan-darija-captions/references/intake.md`](skills/moroccan-darija-captions/references/intake.md). Use a scoped, read-only inventory to identify available local transcription/alignment models and runtimes, relevant provider-credential availability, computer fit for any proposed local setup, and accessible editors/renderers. Do not run model inference, upload media, make a paid API call, install packages, or download weights during discovery. Check credential presence only; never reveal secret values.

Show the user what was found, recommend a route based on the current official provider docs, then ask once for any missing choices: transcription provider, word-alignment fallback, permission to upload audio or spend up to a stated amount, permission to install named packages/models, project/editor destination, full-task check/build/preview/render authorization, and what to do with unresolved words. Skip choices already answered in the prompt or existing project.

After the user confirms, carry those answers through the named task without repeating the same approval request at every stage. Stop only if a new action exceeds the agreed provider, cost, install, or render scope, or a material transcript ambiguity needs the user. Keep the source media unchanged and never invent words or timings.
