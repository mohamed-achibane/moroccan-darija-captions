# Claude adapter

Use the Claude entry skill under `skills/moroccan-darija-captions-claude/`. Claude Code supports skills with a `SKILL.md` file and local project tools. The Claude app/web surface is different; check whether it has access to the video, filesystem, terminal, and editor before promising an edit or render.

Run the shared [`intake.md`](../intake.md) using only the read-only discovery tools the active Claude surface exposes. Claude as the assistant does not prove an Anthropic speech-to-text API or credential is available. Check current official Anthropic docs; if no suitable endpoint is documented, offer discovered local models or an explicitly named external API, and obtain consent for its upload and cost.

Use the current Claude Code skill or plugin installation method. For a manual user skill install, keep the skill folder and its referenced resources together under the user’s Claude skills directory. Do not assume Codex-specific metadata or tools are available in Claude.

Read current [Claude Code skills documentation](https://code.claude.com/docs/en/skills) before giving platform commands.
