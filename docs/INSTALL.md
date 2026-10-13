# Installation by ecosystem

This repository provides a shared router skill plus one platform entry skill for Codex, ChatGPT, Claude, and Gemini. Install the router and the matching entry skill together so the latter can load the shared workflow.

The workflow supports API transcription and local inference. It should first check whether a suitable local model is already installed. If it proposes installing one, it checks the actual operating system, hardware, runtime, and storage needs, then asks before downloading packages or model weights. A local install is optional; API use is a separate choice.

## Codex

Install `moroccan-darija-captions` and `moroccan-darija-captions-codex` from this repository into Codex. With the Skills CLI, the command format is:

```sh
npx skills add mohamed-achibane/moroccan-darija-captions --skill moroccan-darija-captions --skill moroccan-darija-captions-codex --agent codex --global
```

The public version uses a separate name. It does not replace a pre-existing local skill with another name.

## ChatGPT app

This repository has a portable `plugin.json` and ChatGPT-specific entry skill. ChatGPT app support depends on the current product surface, available tools, and account/workspace eligibility. To distribute in the public ChatGPT/Codex plugin directory, submit the packaged plugin through OpenAI’s current portal; GitHub hosting alone does not publish it to that directory. See [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins) and [submission guidance](https://developers.openai.com/plugins/deploy/submission).

If the user is chatting in a surface without local file or command execution, the skill can review supplied content and guide local work, but must not claim to render a local video.

## Claude Code

Install `moroccan-darija-captions` and `moroccan-darija-captions-claude` into Claude Code, or copy both skill directories into a location Claude Code discovers. Follow the current [Claude Code skills guide](https://code.claude.com/docs/en/skills) for user, project, or plugin installation. The Claude app/web is not the same environment as Claude Code; check tool access before promising local editing.

Skills CLI example:

```sh
npx skills add mohamed-achibane/moroccan-darija-captions --skill moroccan-darija-captions --skill moroccan-darija-captions-claude --agent claude-code --global
```

## Gemini CLI

Gemini CLI supports Agent Skills. Its current docs show repository installation through `gemini skills install`; check those docs for current scope and activation behavior. Install the shared router and Gemini entry skill, or clone this repository and link both local skill directories.

```sh
gemini skills install https://github.com/mohamed-achibane/moroccan-darija-captions
```

See [Gemini CLI skill installation](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/using-agent-skills.md). Gemini app/web does not imply local terminal access; use a supported prompt or connected tool when CLI access is unavailable.

## Update or remove

Use the selected ecosystem’s current skill update/removal commands. Before replacing an existing installation, compare its folder name and local changes so a user-specific variant is not overwritten.
