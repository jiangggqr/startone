# Dependency-ordered implementation plan

## Milestone 0 — Runnable foundation

Create FastAPI, SQLite initialization, static app shell, configuration, Demo/real mode indicator, health endpoint, test command and clean README. Do not implement AI or upload processing.

**Status:** Complete and verified on 2026-07-20. The production UI language is English.

## Milestone 1 — Source ingestion and grounding

Implement PDF, Markdown, TXT and pasted-text ingestion; real page or line locations; stable source/chunk IDs; persistence; source inventory; preview; partial-success and parse-error states.

**Status:** Complete and verified on 2026-07-20. No model or external search is used.

## Milestone 2 — Learner setup, coverage and knowledge map

Implement session setup, source coverage, named gaps, 2–5 concept dependency map, initial route and one 60–120 second start action. This milestone creates the shared server-side OpenAI gateway and the first real GPT-5.6 Structured Outputs path, while retaining a deterministic Demo path. Use schema validation and grounded source references.

**Status:** Complete and verified on 2026-07-21. The deterministic Demo path is fully runnable; the real GPT-5.6 path is implemented and contract-tested, while a live smoke test remains pending until a local `OPENAI_API_KEY` is configured.

## Milestone 3 — Production focus-session shell

Implement desktop/tablet/mobile layouts, one active concept, one primary action, compact map, source viewer, visible/optional time, autosave, resume, pause, summary shell, keyboard basics and cross-cutting states.

**Status:** Complete and verified on 2026-07-21. Start/focus drafts are server-versioned with explicit conflict resolution; pause/resume preserves the active concept and timer; the responsive focus workspace and restart summary are fully browser-tested.

## Milestone 4A — Contextual Tutor

Implement source-aware chat, quick actions, free questions, graduated guidance, checking questions, persistence, origin labels and prerequisite-gap signals. Tutor cannot change route or search.

**Status:** Complete and verified on 2026-07-21. Tutor messages persist per active concept; six quick supports and free questions follow a seven-level guidance ladder; every response uses validated source references and explicit source-origin labels; Tutor has no route or search capability.

## Milestone 4B — Quiz and free recall

Implement one-question Quiz, misconception-based distractors, free recall, progressive hints, attempt persistence and source references. No Agent decision in this milestone.

**Status:** Complete and verified on 2026-07-21. Quiz answer keys, misconception targets and recall evaluation points remain server-only; answers and 0–3 hint depth recover across refresh and pause; attempts persist with grounded source references and no evidence, Agent action or search side effect.

## Milestone 4C — Feedback, encouragement, remedial practice and LearningEvidence

Implement structured immediate feedback, specific encouragement, misconception detection, remedial activity and normalized evidence with no recommendation fields.

**Status:** Complete and verified on 2026-07-21. Every submitted Quiz, recall or remedial attempt produces fixed structured feedback and one factual evidence record; Tutor close aggregates a factual boundary record; remediation stays inside the active concept; pause/refresh recovery covers all new states; evidence contains no recommendation fields and creates no Agent decision or search side effect.

## Milestone 5 — Adaptive Planning Agent

Implement bounded action enum, exactly one next decision, learner-facing reason, estimate, override path, prerequisite insertion/return and server-validated transitions.

**Status:** Complete and verified on 2026-07-21. The Agent reads validated `LearningEvidence` as its sole learning-performance basis, proposes exactly one of eight bounded actions, exposes only server-valid alternatives, supports penalty-free override and executes only controlled state transitions. A strict GPT-5.6 function-call contract and a deterministic Demo policy remain visibly separated; `request_search` stops at confirmation and performs no search.

## Milestone 6 — Controlled external search

Implement session permission, runtime confirmation, named gap, Agent request, Responses API web search, selected cited sources, origin labels, mock mode and failure recovery.

**Status:** Complete and verified on 2026-07-21. Search execution revalidates all four gates, real mode requires the Responses API web-search tool and persists only cited public HTTPS results, Demo mode uses a deterministic result set, and selection/ignore/cancel/failure states return safely to the uploaded-material-first learning flow. A dedicated one-source Demo fixture makes the named-gap path reachable without database manipulation.

## Milestone 7 — End-to-end production hardening

Audit and close gaps in loading, empty, error, partial-success, offline and recovery states already implemented with their owning milestones; complete accessibility checks, responsive checks, security/privacy review, browser flow tests, model evals, no-key Demo and real GPT-5.6 smoke test.

**Status:** Implementation and deterministic verification complete on 2026-07-21. The full 43-test suite, cross-milestone browser runs, 390 px/zoom-equivalent audits, security/privacy review and all acceptance-case records pass. Topic-only fallback, data controls, history filters, accessibility preferences and source-location reporting were closed during the audit. The only remaining Milestone 7 gate is one live GPT-5.6 smoke test after a server-side key is configured.

## Milestone 8 — Submission readiness

Finalize README, license, setup, deployment or judge path, sample data, under-three-minute video, Devpost copy, Codex build log and `/feedback` Session ID.
