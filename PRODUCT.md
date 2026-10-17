# Product contract

## Mission

Help creators produce accurate, reviewable Moroccan Darija captions for vertical videos that may switch between Arabic, French, and English, while preserving the source media and the speaker’s wording.

## Users and entry points

- Codex users, ChatGPT app users, Claude users, and Gemini users choose the entry skill for the environment they are using. The entry skill identifies the assistant ecosystem; it does not automatically select a speech provider.
- Gemini users distinguish Gemini CLI from the Gemini app/web; Claude users distinguish Claude Code from the Claude app/web.
- Each user chooses speech recognition and the video editor independently of the assistant ecosystem.

## Source of truth

- The audio is authoritative for the transcript; a reviewed, word-aligned transcript is authoritative for caption text and timing.
- Preserve Darija in Arabic script and spoken French/English in Latin script. Never translate, transliterate, paraphrase, or normalize the speaker’s wording.
- Existing projects keep their own schema and generators. The bundled normalized schema is a fallback, not a forced migration.
- Keep original video, audio, framing, and opening title intact unless the creator asks for a change.

## Quality and safety rules

- Review the complete clip, including the opening, language switches, and ending. Keep wording review separate from timing review. Mark uncertainty instead of fabricating a word or timestamp, and never call model output or alignment a human listening review.
- Before asking workflow preferences, perform a scoped, read-only inventory of available local ASR/alignment resources, relevant provider credential availability, and editor/render tools. Check credential presence only; never reveal secret values or treat a detected credential as consent to upload media or spend money.
- Ask all unanswered provider, alignment, data/cost, installation, delivery, and task-completion authorization choices together once. Carry explicit consent through the named video task; do not repeat approvals for the same authorized actions.
- Treat model language support as a candidate signal, not proof of Moroccan Darija accuracy. Compare current documented options on representative audio when requested.
- Keep API credentials in the chosen provider’s supported secret store. Never put credentials or private source media in GitHub.
- The house style is a selectable default. Use the creator’s requested font, layout, and motion when they differ.
- An assistant must check its actual file, terminal, and rendering capabilities before promising local video edits or exports.
