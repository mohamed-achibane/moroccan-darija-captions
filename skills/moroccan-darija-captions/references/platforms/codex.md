# Codex adapter

Use the Codex skill under `skills/moroccan-darija-captions-codex/` for Codex-specific setup. Codex can use this skill from a local workspace when its configured tools provide access to project files and commands.

The entry skill identifies Codex, so do not ask the user to select an ecosystem. Follow the shared [`intake.md`](../intake.md) before asking for task preferences: inventory reachable local ASR/alignment models and tools, and check only whether relevant provider credentials are available. Never expose secret values. Codex availability does not mean an OpenAI API key exists or that audio upload/API spend is authorized.

Keep the user's pre-existing local skill and its settings intact. Install this public package under a distinct skill name. Read the repository’s `AGENTS.md` and the project’s own instructions before editing. Consent gathered once in the intake covers only the named media checks, preview, build, and render for that task. Use project-approved commands and keep generated MP4 files out of Git unless explicitly requested.

The skill format is compatible with Codex. For ChatGPT/Codex plugin distribution, use the root `plugin.json`; publishing in the OpenAI public plugin directory requires its separate submission and review process.
