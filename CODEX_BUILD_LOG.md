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
- Git commit: `7d3b1b0`
- Goal: make the first learning step durable, resumable and usable across desktop, tablet and mobile without adding Tutor or mastery judgments early
- Codex contribution: added schema version 4; server-versioned drafts; explicit two-copy conflict resolution; start-action completion; one-active-concept initialization; source-backed focus payloads; elapsed/remaining timer state; pause/resume mutation locks; a responsive three-column focus workspace; 390 px bottom session navigation; offline/save status; source-return focus restoration; and a concrete restart summary
- Human product decisions: the Demo route treats Transformer goal as completed orientation and starts active learning at Self-attention; a focus note is an ungraded navigation aid and never LearningEvidence; all user-visible copy remains English and all large backgrounds remain flat colors
- Files changed: focus-state service, schema/API/session serialization, static focus/start/summary UI, automated tests, project status and milestone records
- Verification: 17 automated tests passed; Python compilation, JavaScript syntax and diff hygiene passed; application/test/environment files contained no Chinese UI strings or gradient declarations
- Browser verification: created a new grounded session; completed and server-autosaved the 90-second start answer; entered Self-attention as the only active concept; opened the exact uploaded line reference and returned keyboard focus to the invoking control; autosaved a focus note; paused with the mutation lock; resumed and refreshed with draft, concept and timer intact; saved and exited to a concrete restart action; and resolved a real two-tab draft conflict after comparing both copies
- Responsive verification: at 390 px the Map/Learn/More panels were operable from the fixed bottom navigation, the document width remained exactly 390 px with no horizontal overflow, and visual inspection confirmed solid backgrounds with no large-area gradient
- Problems and corrections: the initial test module import did not resolve under pytest collection and was converted to an explicit test package import; draft conflict QA intentionally used two live pages to prove that no copy is silently overwritten
- Remaining limitations: Tutor is deliberately disclosed as the next Guided Mastery Loop milestone; the environment still has no `OPENAI_API_KEY`, which is not needed for this deterministic milestone

## Milestone 4A — Contextual Tutor

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: `014c34b`
- Goal: add continuous, low-pressure support for the active concept without giving Tutor any planning or search authority
- Codex contribution: added schema version 5, per-concept Tutor threads, ordered persistent messages, six quick support actions, free questions, a seven-level guidance ladder, retry-safe unsent drafts, explicit uploaded/AI-supplement origins, checking questions, factual difficulty signals, bounded source retrieval, server-side source-reference validation, Demo responses and a strict GPT-5.6 Structured Output path
- Human product decisions: Tutor remains an overlay on `learning_concept`; one thread is retained per session/concept and can be closed/reopened without losing history; Tutor close records aggregate signal counts but does not create `LearningEvidence` before Milestone 4C; no Tutor request receives a search or route-change tool
- Files changed: Tutor schema/service/API, typed AI response model, focus/Tutor UI and responsive styles, automated tests, milestone/status/decision records
- Verification: 21 automated tests passed; Demo quick actions, free questions, confusion signals, covered prerequisites, AI supplemental example labels, pause locks, close/reopen persistence and optimistic thread versions passed; a fake Responses client verified `gpt-5.6`, typed `TutorResponseOutput`, `store=False` and absence of any `tools` argument; Python/JavaScript/diff checks passed; application files contained no Chinese UI strings or gradient declarations
- Browser verification: opened Tutor from the dominant focus action; ran a checking question; autosaved and submitted a free confusion message; displayed a factual signal with explicit non-Agent/non-search wording; generated an AI supplemental example with its correct source label; opened an exact source and returned focus to the invoking citation; paused/resumed the same conversation; closed Tutor and restored focus to its trigger
- Responsive verification: the real Tutor flow opened from the 390 px bottom navigation, document width equaled viewport width with no horizontal overflow, and visual inspection confirmed a flat-background full-screen conversation layout
- Problems and corrections: Tutor messages initially used second-resolution timestamps plus UUIDs for ordering, which could reverse a same-turn pair; reads now use SQLite insertion order; the Tutor source viewer initially displayed an incorrect “Back to library” label even though it returned correctly, and was corrected to “Back to Tutor” with focus restoration rechecked
- Remaining limitations: `LearningEvidence`, structured feedback, Quiz, recall and remediation intentionally begin in Milestones 4B/4C; the live GPT-5.6 smoke test remains pending a deployment-only API key

## Milestone 4B — Quiz and free recall

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: Milestone 4B focused commit (this commit)
- Goal: add one-question Quiz and free recall with progressive support and durable attempts while preserving the Tutor/Agent boundary
- Codex contribution: added schema version 6, typed Quiz/recall outputs, current-concept activity generation, server-only evaluation keys, misconception-based Quiz distractors, three-level hints, activity-linked drafts, versioned hint reveals, durable attempts, pause/refresh recovery, source return and responsive English practice screens
- Human product decisions: answers and scoring rubrics remain hidden until feedback; a 4B submission records facts but creates no `LearningEvidence`, Agent decision or search request; Tutor remains the dominant recommended focus action while Quiz and recall are visually secondary
- Files changed: activity schema/service/API, typed AI models, focus state support, static practice UI, automated tests, README, status and decision records
- Verification: 24 automated tests passed; Quiz answer keys, misconception tags and option explanations were absent from pre-feedback API payloads; recall key points and misconception patterns stayed server-only; activity draft conflicts, hints, pause/resume, attempts, source validation and boundary flags passed; a fake Responses client verified `gpt-5.6`, typed `QuizActivityOutput`, `store=False` and no `tools` argument; JavaScript syntax and diff hygiene passed; application/test files contained no Chinese UI strings or gradient declarations
- Browser verification: launched Quiz from the active concept, selected an answer, revealed a hint, restored the same answer and hint through a fresh page, opened the exact uploaded source and returned to practice, paused/resumed, submitted without exposing correctness, returned to the concept, then created and submitted a free recall with two progressive hints; all browser requests completed without server errors
- Responsive verification: the complete recall screen and fixed Practice navigation were exercised at 390 px; visual inspection caught a clipped header badge, the activity header was changed to a stacked mobile layout, and the corrected screen was rechecked with flat solid backgrounds and no visible critical horizontal clipping
- Problems and corrections: a stale browser-control tab stopped accepting clicks during repeated QA, so the same saved practice was reopened in a fresh tab and recovery was confirmed; the first mobile activity heading placed two non-wrapping badges in one row, which was corrected before completion
- Remaining limitations: immediate correctness/coverage feedback, encouragement, remediation and `LearningEvidence` intentionally begin in Milestone 4C; the live GPT-5.6 smoke test remains pending a deployment-only API key

## Milestone 4C — Feedback, remediation and LearningEvidence

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: Milestone 4C focused commit (this commit)
- Goal: close the Guided Mastery Loop with immediate structured feedback, specific encouragement, targeted remediation and normalized factual evidence while preserving the Agent/search boundary
- Codex contribution: added schema version 7; strict feedback and remedial output models; deterministic and real GPT-5.6 generation paths; fixed five-part feedback; Quiz/recall/remedial evaluation; misconception tags; five rotating remedial strategies; Tutor-close aggregation; recommendation-free `LearningEvidence`; durable feedback/remedial/evidence-ready states; and responsive English screens
- Human product decisions: Feedback's next micro-action remains local to the active concept; `LearningEvidence` has no recommendation fields; ungraded Tutor boundaries use `outcome=unresolved`; finishing feedback means evidence is ready, not that the Agent has already decided; no 4C operation can search
- Files changed: mastery schema/service/API, typed AI models, activity/Tutor/focus state handling, feedback/remedial/evidence UI, automated tests, README and milestone records
- Verification: 27 automated tests passed; fake Responses clients verified `gpt-5.6`, typed `FeedbackOutput` and `RemedialActivityOutput`, `store=False` and no `tools` argument; Quiz/recall/remedial evidence, Tutor-close evidence, idempotent feedback, pause locks and database column exclusions passed; Python compilation and JavaScript syntax passed
- Browser verification: restored a previously submitted recall and generated complete feedback; completed the evidence boundary; built a fresh source-grounded session; submitted a misconception-based Quiz answer; reviewed all five feedback sections and factual evidence; paused/resumed the same feedback; started, restored and completed a one-sentence remedial task; and returned to structured remedial feedback without server errors
- Responsive verification: the evidence-ready view was visually inspected at 390 px with no critical horizontal clipping; desktop feedback used a stable two-column layout with a sticky evidence panel; all backgrounds remained flat solid colors with no gradients
- Problems and corrections: browser QA found that remedial input still said “2–3 sentence explanation” and omitted its completion condition; the view now uses a one-sentence label and shows the condition. The deterministic evaluator initially reused the three-point Self-attention recall heuristic for one-point remediation; it now evaluates the remedial rubric independently
- Remaining limitations: the Adaptive Planning Agent is intentionally not created until Milestone 5; controlled external search remains unavailable until Milestone 6; the live GPT-5.6 smoke test still requires a server-side deployment key
