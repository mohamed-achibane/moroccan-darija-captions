# Gemini adapter

Use the Gemini entry skill under `skills/moroccan-darija-captions-gemini/`. If the user means Gemini CLI, use its Agent Skills installation and activation flow. If they mean Gemini app/web, do not assume local `SKILL.md` files or shell access; provide the relevant instructions in a supported prompt/project or use connected tools.

After identifying the accessible Gemini surface, follow the shared [`intake.md`](../intake.md). Check for local ASR/alignment tools and whether a Gemini API credential is available without revealing its value. Gemini as the assistant does not authorize sending audio to the Gemini API or incurring API charges; check the current transcription and word-timestamp docs before offering that route.

Check the current Gemini CLI documentation for skill install and activation commands. Skill activation is subject to Gemini CLI’s own consent behavior. Do not expose API keys in chat or source control.

Read the current [Gemini CLI Agent Skills guide](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/using-agent-skills.md) before giving platform commands.
