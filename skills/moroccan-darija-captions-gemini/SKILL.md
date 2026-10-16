---
name: moroccan-darija-captions-gemini
description: Use the Moroccan Darija captions workflow with Gemini CLI or the Gemini app, choosing current speech recognition separately from WhisperX alignment and the video editor.
---

# Moroccan Darija Captions for Gemini

This is the Gemini entry skill. Read the shared workflow at `../moroccan-darija-captions/SKILL.md` and its Gemini adapter at `../moroccan-darija-captions/references/platforms/gemini.md`, then follow them for the whole task.

This entry skill establishes Gemini as the assistant ecosystem. If the environment does not reveal whether the user means Gemini CLI or Gemini app/web, ask only that platform-access question. Then follow the shared [one-time intake](../moroccan-darija-captions/references/intake.md): discover usable local models and safe credential availability before presenting Gemini transcription, local, or other authorized API routes together.

Gemini as the assistant does not automatically authorize the Gemini transcription API, audio upload, or API charges. Check current official docs for the available transcription and word-timestamp options before recommending them.

Use current Gemini CLI skill-install and activation guidance. Check whether the active Gemini surface can read the local media and run the selected editor before promising a complete render.
