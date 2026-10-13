---
name: moroccan-darija-captions-gemini
description: Use the Moroccan Darija captions workflow with Gemini CLI or the Gemini app, choosing current speech recognition separately from WhisperX alignment and the video editor.
---

# Moroccan Darija Captions for Gemini

This is the Gemini entry skill. Read the shared workflow at `../moroccan-darija-captions/SKILL.md` and its Gemini adapter at `../moroccan-darija-captions/references/platforms/gemini.md`, then follow them for the whole task.

The shared workflow asks which assistant ecosystem first when the user has not said. Since this entry skill is the Gemini option, ask whether they mean Gemini CLI or Gemini app/web if unclear. Transcription provider and editor remain separate choices; Gemini can be the assistant without requiring that its transcription API is selected.

Use current Gemini CLI skill-install and activation guidance. Check whether the active Gemini surface can read the local media and run the selected editor before promising a complete render.
