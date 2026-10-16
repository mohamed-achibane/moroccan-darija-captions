---
name: moroccan-darija-captions-claude
description: Use the Moroccan Darija captions workflow in Claude Code or Claude, with mixed Arabic/French/English transcription, word timing, and HyperFrames or Remotion output.
---

# Moroccan Darija Captions for Claude

This is the Claude entry skill. Read the shared workflow at `../moroccan-darija-captions/SKILL.md` and its Claude adapter at `../moroccan-darija-captions/references/platforms/claude.md`, then follow them for the whole task.

This entry skill establishes Claude as the assistant ecosystem. If the environment does not reveal whether the user means Claude Code or the Claude app/web, ask only that platform-access question. Do not assume Claude has local file or terminal access. Then follow the shared [one-time intake](../moroccan-darija-captions/references/intake.md) to discover the available local models, safe credential availability, and editing tools before presenting one bundled set of remaining choices.

Do not offer a Claude transcription model unless current official Anthropic documentation confirms a suitable speech-to-text route. If it does not, present the discovered local models or a named external transcription API as separate choices, with explicit audio-upload and cost consent.

Use current Claude skill/plugin guidance for installation. If Claude cannot access local video or run the chosen editor, say what is missing and offer a workflow the user can run locally.
