# Repository guidance

This repository distributes a reusable, multi-ecosystem caption workflow. Keep changes small and focused on the shared skill, platform entry skills, documentation, or bundled helper scripts.

## Before changing files

- Read `README.md`, `START-HERE.md`, and the relevant shared or platform skill.
- Keep each platform’s setup guidance in its adapter or install notes; do not assume all assistants share the same tools or skill format.
- Keep the transcript, timing, and renderer responsibilities distinct. Never invent word timings or claim structural checks prove audio accuracy.

## Safety and compatibility

- Never include API keys, personal video/audio, transcripts from private media, or generated renders in this repository.
- Keep platform-specific resources referenced from the correct skill and document when skills must be installed together.
- Check official provider and ecosystem documentation before documenting time-sensitive model names, features, or install commands.
- Preserve the author’s approved caption treatment as an optional preset; honor each user’s explicit choices.

## Changes and reporting

- Inspect the final diff and report exactly which checks were or were not run.
- Do not commit generated video files. Keep sample transcript content synthetic and clearly illustrative.
- Do not modify a user’s separately installed skill when preparing or installing this public package.
