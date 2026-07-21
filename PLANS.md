# Dependency-ordered implementation plan

## Milestone 0 — Runnable foundation

Create FastAPI, SQLite initialization, static app shell, configuration, health endpoint, test command and clean README. Do not implement AI or upload processing.

**Status:** Complete and verified on 2026-07-20. The production UI language is English.

## Milestone 1 — Source ingestion and grounding

Implement PDF, Markdown, TXT and pasted-text ingestion; real page or line locations; stable source/chunk IDs; persistence; source inventory; preview; partial-success and parse-error states.

**Status:** Complete and verified on 2026-07-20. No model or network tool is used.

## Milestone 2 — Automatic material analysis, coverage and knowledge map

Implement material-driven source coverage, named gaps, an AI-selected learning focus and a 2–5 concept dependency map with beginner-friendly explanations, key points and examples. No learner setup form or pre-test is allowed. This milestone creates the shared server-side OpenAI gateway and the first real GPT-5.6 Structured Outputs path while retaining deterministic test fixtures. Use schema validation and grounded source references.

**Status:** Complete and verified on 2026-07-21. Upload leads to AI coverage, focus and map generation, then directly to the first concept explanation. Calibration begins only after guided practice produces validated evidence. The real GPT-5.6 path is implemented and live-smoke-tested, with deterministic behavior isolated to tests.

## Milestone 3 — Production focus-session shell

Implement desktop/tablet/mobile layouts, one active concept, one primary action, compact map, lightweight inline source citations, visible/optional time, autosave, resume, pause, summary shell, keyboard basics and cross-cutting states.

**Status:** Complete and verified on 2026-07-21. Start/focus drafts are server-versioned with explicit conflict resolution; pause/resume preserves the active concept and timer; the responsive focus workspace and restart summary are fully browser-tested.

## Milestone 4A — Contextual Tutor

Implement source-aware chat, quick actions, free questions, graduated guidance, checking questions, persistence, origin labels and prerequisite-gap signals. Tutor cannot change route, request material or access outside information.

**Status:** Complete and verified on 2026-07-21. Tutor messages persist per active concept; six quick supports and free questions follow a seven-level guidance ladder; every response uses validated source references and explicit source disclosure; Tutor has no route, upload-request or outside-information capability.

## Milestone 4B — Quiz and free recall

Implement a three-question single-select Quiz, misconception-based distractors, one free-recall response, progressive hints, attempt persistence and source references. No Agent decision in this milestone.

**Status:** Complete and verified on 2026-07-22. Each concept Quiz contains exactly three single-select questions covering definition, mechanism and application; free recall remains one response. Answer keys, misconception targets and recall evaluation points remain server-only; all answers and 0–3 hint depth recover across refresh and pause. The learner sees a compact test, optional inline hints, per-question review and no repeated file-location or system-boundary panels.

## Milestone 4C — Feedback, encouragement, remedial practice and LearningEvidence

Implement structured immediate feedback, specific encouragement, misconception detection, remedial activity and normalized evidence with no recommendation fields.

**Status:** Complete and verified on 2026-07-22. Every submitted Quiz, recall or remedial attempt still produces structured feedback and one factual evidence record, but the UI compresses it into a familiar result, answer review, short explanation and Keep going. Evidence remains recommendation-free and is not exposed as a separate learner task.

## Milestone 5 — Adaptive Planning Agent

Implement a bounded action enum, exactly one next decision, automatic execution of safe actions, prerequisite insertion/return and server-validated transitions. Do not add a learner-facing decision, alternative-path or separate gap-confirmation page; `request_more_material` may preserve the concept and open the existing upload area only when a validated named gap blocks learning.

**Status:** Complete and verified on 2026-07-22. The Agent reads validated `LearningEvidence` as its sole learning-performance basis and proposes exactly one bounded action. Keep going requests that decision and applies safe actions automatically without a separate decision page. A validated blocking gap can produce `request_more_material`; no Agent action can search the web.

## Milestone 6 — Material-gap recovery

Implement validated named gaps, the bounded `request_more_material` Agent action, a concise inline explanation inside the existing upload area, a continue-with-current-scope path, and recovery without losing progress.

**Status:** Superseded by the final product decision on 2026-07-22. The earlier network-search implementation was removed from the learner product. StartOne now keeps uploaded material as the only source: a validated blocking gap can only ask the learner to upload relevant material or continue within the current scope. No model call receives a web-search tool.

## Milestone 7 — End-to-end production hardening

Audit and close gaps in loading, empty, error, partial-success, offline and recovery states already implemented with their owning milestones; complete accessibility checks, responsive checks, security/privacy review, browser flow tests, deterministic model evals and a real GPT-5.6 smoke test.

**Status:** Complete and verified on 2026-07-21. The regression suite, cross-milestone browser runs, 390 px/zoom-equivalent audits, security/privacy review and acceptance records pass. An isolated real GPT-5.6 smoke flow passed source coverage, knowledge map, Tutor, Quiz, structured feedback and bounded Agent decisions.

## Milestone 8 — Submission readiness

Finalize README, license, setup, deployment or judge path, sample data, under-three-minute video, Devpost copy, Codex build log and `/feedback` Session ID.

**Status:** Local release and submission package complete on 2026-07-21. Version 1.0.0 includes public workspace quotas, Docker/Render deployment files, CI, MIT license, English README, judge instructions, Devpost copy, a timed 2:50 video script, final checklist, verified `/feedback` Session ID and a passing isolated live GPT-5.6 core-flow smoke test. Remaining external gates are a public repository and real GPT-5.6 deployment, video recording/upload, and the user-confirmed final Devpost action.

## Product refinement — StartOne Momentum Loop

Rename the learner-facing product to StartOne and make the initiation-to-completion mechanism explicit: one-click preparation, a connected visual knowledge map, one-concept focus, relationship visualization, a memory anchor, immediate retrieval, truthful small-win feedback and automatic application of the Agent's one safe next action. Uploaded material remains the only learning source.

**Status:** Implemented in the production client and aligned across the core specification, prototype, tests and submission artifacts on 2026-07-22.
