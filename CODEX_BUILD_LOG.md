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
- Git commit: `54258dd`
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
- Git commit: `04447e6`
- Goal: accept PDF, Markdown, TXT and pasted text while preserving real, server-validated locations
- Codex contribution: added anonymous workspace isolation, version-2 SQLite source schema, UUID/checksum blob storage, structural parsers, stable chunk IDs, local source retrieval, source APIs, retry/cancel/delete behaviors, an English upload inventory and a verifiable preview UI
- Human product decisions: every user-visible product string is English; the visual system uses flat backgrounds and does not use large-area gradients
- Files changed: source/config/database/API modules, static app, source tests, environment and dependency declarations, status and decision records
- Verification: 9 automated tests passed; Markdown heading/line locators, PDF page locators, scanned-PDF failure, pasted paragraph locators, partial multi-file success, stable retry IDs, local retrieval, workspace isolation and blob cleanup were exercised; Python and JavaScript syntax passed; app source contained no Chinese UI strings or gradient declarations
- Browser verification: real pasted-text creation → parsing → inventory → two-paragraph preview passed; delete-confirmation cancel returned focus to the Remove trigger; 390 px viewport had 390 px document width with no horizontal overflow; browser console reported zero errors
- Problems and corrections: the in-app browser does not support automated native file selection, so PDF/Markdown/TXT multipart upload is covered by API integration tests while the complete pasted-source UI path is covered in-browser; stale Milestone 0 data copy and an overly prominent disabled future action were corrected
- Remaining limitations: source coverage and session setup begin in Milestone 2; no OpenAI call exists in Milestone 1; the current environment does not yet contain `OPENAI_API_KEY`

## Milestone 2 — Learner setup, coverage and knowledge map

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: `c2b2304`
- Goal: turn ready uploaded sources into an English session setup, grounded coverage review, 2–5 concept map, adjustable route and one 60–120 second start action
- Codex contribution: added schema version 3, optimistic setup persistence, candidate SourceGap records, typed coverage/map schemas, a shared server-side Responses API gateway, deterministic Demo generation, real GPT-5.6 configuration, source-reference validation, AI activity metadata, Demo material loading and the complete pre-learning browser flow
- Human product decisions: the production UI and generated learning content stay in English; all major backgrounds are flat colors; the OpenAI key is configured only in local/deployment environment variables and is never pasted into chat or committed
- Files changed: AI and learning modules, settings, database migration, API routes, static UI, tests, environment template, dependency list and milestone records
- Verification: 14 automated tests passed; OpenAI SDK 2.46.0 generated strict response formats for both Pydantic output types; Demo setup → coverage → map → route adjustment → confirmation passed; real mode without a key returned an explicit recoverable error; invalid model source references were rejected before persistence; malformed setup requests used the product error envelope
- Browser verification: loaded both real Demo Markdown sources, reviewed exact heading/line citations, saved English setup, generated coverage and a five-concept route, shortened/restored/confirmed the route, saved/restored the first-action draft, opened a source from the map and returned focus to the exact trigger; 390 px viewport had 390 px document width with no horizontal overflow; browser console reported zero errors; visual inspection confirmed solid backgrounds and no large-area gradients
- Official API alignment: implementation uses the Responses API `responses.parse` path, `gpt-5.6` server default, low reasoning effort, `store=False`, a privacy-preserving safety identifier and Pydantic Structured Outputs; the OpenAI SDK was inspected locally to confirm these parameters
- Problems and corrections: local ports 8000 and 8010 were already occupied, so browser verification used 8020; a source-reference preview initially lacked a direct return path, so it now returns to coverage/map and restores focus to the invoking citation control
- Remaining limitations: the environment has no `OPENAI_API_KEY`, so the live GPT-5.6 smoke test is deferred to final hardening; the start-action answer is currently restored from local storage and becomes a versioned server draft in Milestone 3; no external search tool is exposed in this milestone

## Milestone 3 — Production focus-session shell

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: Milestone 3 focused commit (this commit)
- Goal: make the first learning step durable, resumable and usable across desktop, tablet and mobile without adding Tutor or mastery judgments early
- Codex contribution: added schema version 4; server-versioned drafts; explicit two-copy conflict resolution; start-action completion; one-active-concept initialization; source-backed focus payloads; elapsed/remaining timer state; pause/resume mutation locks; a responsive three-column focus workspace; 390 px bottom session navigation; offline/save status; source-return focus restoration; and a concrete restart summary
- Human product decisions: the Demo route treats Transformer goal as completed orientation and starts active learning at Self-attention; a focus note is an ungraded navigation aid and never LearningEvidence; all user-visible copy remains English and all large backgrounds remain flat colors
- Files changed: focus-state service, schema/API/session serialization, static focus/start/summary UI, automated tests, project status and milestone records
- Verification: 17 automated tests passed; Python compilation, JavaScript syntax and diff hygiene passed; application/test/environment files contained no Chinese UI strings or gradient declarations
- Browser verification: created a new grounded session; completed and server-autosaved the 90-second start answer; entered Self-attention as the only active concept; opened the exact uploaded line reference and returned keyboard focus to the invoking control; autosaved a focus note; paused with the mutation lock; resumed and refreshed with draft, concept and timer intact; saved and exited to a concrete restart action; and resolved a real two-tab draft conflict after comparing both copies
- Responsive verification: at 390 px the Map/Learn/More panels were operable from the fixed bottom navigation, the document width remained exactly 390 px with no horizontal overflow, and visual inspection confirmed solid backgrounds with no large-area gradient
- Problems and corrections: the initial test module import did not resolve under pytest collection and was converted to an explicit test package import; draft conflict QA intentionally used two live pages to prove that no copy is silently overwritten
- Remaining limitations: Tutor is deliberately disclosed as the next Guided Mastery Loop milestone; the environment still has no `OPENAI_API_KEY`, which is not needed for this deterministic milestone
