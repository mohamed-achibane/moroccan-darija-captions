---
name: moroccan-darija-captions-chatgpt
description: Use Moroccan Darija Captions in the ChatGPT app or an OpenAI plugin workflow; check tool access before promising local transcription, editing, or rendering.
---

# Moroccan Darija Captions for ChatGPT

This is the ChatGPT entry skill. Read the shared workflow at `../moroccan-darija-captions/SKILL.md` and its ChatGPT adapter at `../moroccan-darija-captions/references/platforms/chatgpt.md`, then follow them for the whole task.

The shared workflow asks which assistant ecosystem first when the user has not said. Since this entry skill is the ChatGPT option, continue with ChatGPT once selected. Transcription provider and editor remain separate choices; ask if either is missing.

Before accepting a local editing task, identify which files, API, connected app, and rendering tools are actually available in this ChatGPT surface. If it cannot access the source video or run HyperFrames/Remotion, do not claim to have edited or rendered it. Never ask for provider keys in chat. A public GitHub repository is not itself a ChatGPT app installation; the OpenAI plugin route has its own import and review process.
