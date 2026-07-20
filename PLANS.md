# Dependency-ordered implementation plan

## Milestone 0 — Runnable foundation

Create FastAPI, SQLite initialization, static app shell, configuration, Demo/real mode indicator, health endpoint, test command and clean README. Do not implement AI or upload processing.

**Status:** Complete and verified on 2026-07-20. The production UI language is English.

## Milestone 1 — Source ingestion and grounding

Implement PDF, Markdown, TXT and pasted-text ingestion; real page or line locations; stable source/chunk IDs; persistence; source inventory; preview; partial-success and parse-error states.

**Status:** In progress.

## Milestone 2 — Learner setup, coverage and knowledge map

Implement session setup, source coverage, named gaps, 2–5 concept dependency map, initial route and one 60–120 second start action. This milestone creates the shared server-side OpenAI gateway and the first real GPT-5.6 Structured Outputs path, while retaining a deterministic Demo path. Use schema validation and grounded source references.

## Milestone 3 — Production focus-session shell

Implement desktop/tablet/mobile layouts, one active concept, one primary action, compact map, source viewer, visible/optional time, autosave, resume, pause, summary shell, keyboard basics and cross-cutting states.

## Milestone 4A — Contextual Tutor

Implement source-aware chat, quick actions, free questions, graduated guidance, checking questions, persistence, origin labels and prerequisite-gap signals. Tutor cannot change route or search.

## Milestone 4B — Quiz and free recall

Implement one-question Quiz, misconception-based distractors, free recall, progressive hints, attempt persistence and source references. No Agent decision in this milestone.

## Milestone 4C — Feedback, encouragement, remedial practice and LearningEvidence

Implement structured immediate feedback, specific encouragement, misconception detection, remedial activity and normalized evidence with no recommendation fields.

## Milestone 5 — Adaptive Planning Agent

Implement bounded action enum, exactly one next decision, learner-facing reason, estimate, override path, prerequisite insertion/return and server-validated transitions.

## Milestone 6 — Controlled external search

Implement session permission, runtime confirmation, named gap, Agent request, Responses API web search, selected cited sources, origin labels, mock mode and failure recovery.

## Milestone 7 — End-to-end production hardening

Audit and close gaps in loading, empty, error, partial-success, offline and recovery states already implemented with their owning milestones; complete accessibility checks, responsive checks, security/privacy review, browser flow tests, model evals, no-key Demo and real GPT-5.6 smoke test.

## Milestone 8 — Submission readiness

Finalize README, license, setup, deployment or judge path, sample data, under-three-minute video, Devpost copy, Codex build log and `/feedback` Session ID.
