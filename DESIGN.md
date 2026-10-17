# Listening-review interface

## Purpose

The generated listening-review page helps a person compare each transcript word and its timing with local audio. It is a private, temporary review aid, not a video editor or a public web app.

## Interaction rules

- Keep all audio local by default. The page has no network calls and does not edit the source media or transcript.
- Show the spoken word, nearby transcript context, time range, language, and any machine-generated review flags together.
- Let the reviewer play the word with adjustable surrounding context at normal or slightly reduced speed.
- Record wording and timing decisions independently. A low model score is a reason to listen, not evidence that the caption is wrong.
- Keep every item available for full-clip review; filtering to flagged items is a convenience, not proof that unflagged words are correct.
- Export a separate decision ledger. Never silently overwrite transcript data or mark a review complete when decisions are pending or uncertain.
- Use native text direction for Arabic and isolate interface labels from transcript reading order.

## Visual direction

Use a calm, high-contrast page with readable controls and clear time labels. Avoid decorative styling, motion, analytics, and remote fonts or scripts. The generated page should work as a local static file in a current browser.
