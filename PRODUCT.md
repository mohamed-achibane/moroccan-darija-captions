# Product contract

## Mission

Help creators produce accurate, reviewable Moroccan Darija captions for vertical videos that may switch between Arabic, French, and English, while preserving the source media and the speaker’s wording.

## Users and entry points

- Codex users, ChatGPT app users, Claude users, and Gemini users choose the entry skill for the environment they are using.
- Gemini users distinguish Gemini CLI from the Gemini app/web; Claude users distinguish Claude Code from the Claude app/web.
- Each user chooses speech recognition and the video editor independently of the assistant ecosystem.

## Source of truth

- The audio is authoritative for the transcript; a reviewed, word-aligned transcript is authoritative for caption text and timing.
- Preserve Darija in Arabic script and spoken French/English in Latin script. Never translate, transliterate, paraphrase, or normalize the speaker’s wording.
- Existing projects keep their own schema and generators. The bundled normalized schema is a fallback, not a forced migration.
- Keep original video, audio, framing, and opening title intact unless the creator asks for a change.

## Quality and safety rules

- Review the complete clip, including the opening, language switches, and ending. Mark uncertainty instead of fabricating a word or timestamp.
- Treat model language support as a candidate signal, not proof of Moroccan Darija accuracy. Compare current documented options on representative audio when requested.
- Keep API credentials in the chosen provider’s supported secret store. Never put credentials or private source media in GitHub.
- The house style is a selectable default. Use the creator’s requested font, layout, and motion when they differ.
- An assistant must check its actual file, terminal, and rendering capabilities before promising local video edits or exports.
