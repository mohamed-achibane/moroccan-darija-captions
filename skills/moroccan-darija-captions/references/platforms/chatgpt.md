# ChatGPT app adapter

Use the ChatGPT entry skill under `skills/moroccan-darija-captions-chatgpt/`. ChatGPT and Codex can use skills bundled in an OpenAI plugin, but access to local files, shells, connected apps, and renderers depends on the selected ChatGPT surface and tools.

Follow the shared [`intake.md`](../intake.md) after checking the capabilities actually exposed by the active ChatGPT surface. If it cannot inspect the computer, do not claim to have inventoried local models or credentials; ask only for missing facts that block the requested route. A ChatGPT plan is not an OpenAI API key.

Do not promise a local edit or fresh render from a chat-only surface. If the available tools cannot read local media or run the selected editor, explain that boundary and provide a usable workflow or use an authorized connected tool. Check provider credential availability without printing secret values. Do not treat a detected key as permission to upload audio or spend money, and do not ask users to paste API keys into chat.

The GitHub repository includes `plugin.json` for packaging. A GitHub repository is not automatically installed into ChatGPT. Public directory distribution requires submitting the plugin through OpenAI’s current portal and passing review; until then, use the current documented import or team marketplace route. [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins), [plugin quickstart](https://developers.openai.com/plugins/quickstart).
