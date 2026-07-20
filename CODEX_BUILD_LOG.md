# Codex build log

Record one section after each verified milestone.

## Specification and prototype baseline

- Status: complete
- Application code: not started
- Date: 2026-07-20
- Baseline commit: `specification and UX prototype baseline` (this baseline commit)
- Main Codex thread/session: current StartFrame Agent task
- Decisions resolved: four search gates; Evidence-only learning judgment; local vs global next action; anonymous workspace isolation; file storage/delete/export; source location schemes; pause/conflict recovery; normal/search Demo fixtures; Milestone 2 real-model entry
- Competition verification: OpenAI Build Week homepage and Official Rules reviewed
- Verification: 18 numbered specs present; 22 prototype screens; navigation targets valid; prototype JavaScript parses; manifest hashes regenerated

## Milestone 0 — Runnable foundation

- Status: complete
- Date: 2026-07-20
- Codex thread/session: current StartFrame Agent task
- Git commit: pending at time of this log entry
- Goal: create a runnable, testable foundation without uploads or model calls
- Codex contribution: implemented FastAPI entry point, environment settings, SQLite schema initialization, security headers, health endpoint, static responsive shell and automated tests
- Human product decision: all user-visible product content must be English; Chinese remains internal specification language only
- Files changed: `app/`, `tests/`, `requirements.txt`, `.env.example`, `README.md`, project status and decision records
- Verification: Python 3.13 virtual environment; 2 automated tests passed; Python and JavaScript syntax passed; desktop and 390 px responsive layouts inspected in the in-app browser; primary dialog exercised; browser console reported zero errors; application source scanned for Chinese UI text with no matches
- Problems and corrections: default Python was 3.9, so the existing Python 3.13 runtime was used; port 8000 was occupied by another local project, so browser verification used port 8010 while the documented/default StartFrame port remains 8000; the first UI draft was Chinese and was corrected immediately to English across UI, runtime states, tests and the governing decision record
- Remaining limitations: upload and learning workflows intentionally begin in Milestone 1; no OpenAI call exists in this milestone

## Milestone template

### Date and milestone
- Date:
- Milestone:
- Codex thread/session:
- Git commit:

### Goal

### Codex contribution

### Human product decisions

### Files changed

### Verification results

### Problems and corrections

### Remaining limitations

## Milestone 1 — Source ingestion and grounding

- Status: complete
- Date: 2026-07-20
- Codex thread/session: current StartFrame Agent task
- Git commit: pending at time of this log entry
- Goal: accept PDF, Markdown, TXT and pasted text while preserving real, server-validated locations
- Codex contribution: added anonymous workspace isolation, version-2 SQLite source schema, UUID/checksum blob storage, structural parsers, stable chunk IDs, local source retrieval, source APIs, retry/cancel/delete behaviors, an English upload inventory and a verifiable preview UI
- Human product decisions: every user-visible product string is English; the visual system uses flat backgrounds and does not use large-area gradients
- Files changed: source/config/database/API modules, static app, source tests, environment and dependency declarations, status and decision records
- Verification: 9 automated tests passed; Markdown heading/line locators, PDF page locators, scanned-PDF failure, pasted paragraph locators, partial multi-file success, stable retry IDs, local retrieval, workspace isolation and blob cleanup were exercised; Python and JavaScript syntax passed; app source contained no Chinese UI strings or gradient declarations
- Browser verification: real pasted-text creation → parsing → inventory → two-paragraph preview passed; delete-confirmation cancel returned focus to the Remove trigger; 390 px viewport had 390 px document width with no horizontal overflow; browser console reported zero errors
- Problems and corrections: the in-app browser does not support automated native file selection, so PDF/Markdown/TXT multipart upload is covered by API integration tests while the complete pasted-source UI path is covered in-browser; stale Milestone 0 data copy and an overly prominent disabled future action were corrected
- Remaining limitations: source coverage and session setup begin in Milestone 2; no OpenAI call exists in Milestone 1; the current environment does not yet contain `OPENAI_API_KEY`
