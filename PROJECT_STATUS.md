# Project status

## Current state

- Product specification: complete
- UI/UX information architecture: complete
- Clickable low-fidelity prototype: complete
- Production UX and accessibility rules: complete
- Data, AI and API contracts: complete
- Acceptance scenarios and Codex prompts: complete
- Milestone 0 application foundation: complete
- Milestone 1 source ingestion and grounding: complete
- Milestone 2 learner setup, coverage and knowledge map: complete
- Milestone 3 production focus-session shell: complete
- Milestone 4A contextual Tutor: complete
- Milestone 4B Quiz and free recall: complete
- Milestone 4C feedback, remediation and LearningEvidence: complete
- Milestone 5 Adaptive Planning Agent: complete
- Production UI language: English

## What the prototype is

`prototype/startframe_lowfi_prototype.html` is a self-contained clickable design artifact. It demonstrates all major screens, the main flow and representative state/recovery branches. The numbered UX specs and evals remain authoritative for the complete production state matrix. It is not the production application and should not be deployed as the final project.

## Implemented foundation

- Python 3.11+ FastAPI/Uvicorn service and versioned SQLite initialization
- Static responsive application shell with accessible landmarks, controls and dialog
- Visible Demo/live-model mode and `GET /api/health`
- Empty state, offline health state and honest not-yet-implemented state
- Automated foundation tests and real desktop/mobile browser inspection
- Anonymous workspace Cookie isolation and private UUID-based source storage
- PDF, Markdown, TXT and pasted-text parsing with real source locations
- Stable source/chunk IDs, checksums, local retrieval, retry and source deletion
- Source inventory, preview, empty/error/partial-success/offline/recovery UI states
- English learner setup with local draft recovery and optimistic server versioning
- Grounded source coverage with candidate gaps that never authorize search
- A 2–5 concept dependency map, adjustable route and one 60–120 second start action
- Shared server-side GPT-5.6 Responses API gateway with Pydantic Structured Outputs
- Server validation of every generated source/chunk reference before persistence or rendering
- Explicit Demo/live-model separation, AI activity metadata and recoverable no-key/model errors
- Server-versioned start-action and focus-note drafts with visible save/offline/failure/conflict states
- Explicit two-copy draft conflict comparison and user-selected resolution
- One-current-concept focus workspace with compact route, source-backed explanation and one dominant action
- Session timer, optional hiding, pause/resume mutation lock and refresh-safe restoration
- Desktop three-column, tablet reflow and 390 px mobile session navigation
- Saved-exit summary with a concrete next restart action
- Current-concept Tutor with persisted per-concept conversation and retry-safe unsent drafts
- Six concrete Tutor quick actions, free questions and a visible seven-level guidance ladder
- Strict typed Tutor responses with validated source references and explicit uploaded/AI-supplement labels
- Factual confusion/prerequisite signals that are visibly not Agent decisions or search requests
- Tutor pause/resume, refresh recovery, source-view return focus and full-screen 390 px mobile flow
- Real GPT-5.6 Tutor contract path with no tools exposed; deterministic Demo Tutor remains visibly labeled
- One-question Quiz with server-only answer keys and misconception-based distractors
- Free recall with server-only key points, acceptable paraphrases and misconception patterns
- Progressive 0–3 hint disclosure with saved depth, answer autosave and explicit conflict recovery
- Persistent activity attempts with source references, pause/refresh recovery and no premature evidence or Agent decision
- Strict GPT-5.6 Quiz/recall Structured Output contracts with deterministic, visibly labeled Demo activities
- Full-screen practice flows with English-only copy, flat backgrounds and a verified 390 px layout
- Fixed five-part feedback: mastered points, missing/unclear points, compact correction, specific encouragement and one current-concept micro-action
- Server-validated factual `LearningEvidence` for Quiz, recall, remedial and Tutor-close boundaries with no recommendation columns
- Targeted remedial practice with five bounded strategy types and no immediate strategy repetition after an unsuccessful result
- Durable `feedback_shown`, `remedial_practice` and `evidence_ready` states with pause/refresh recovery
- Strict GPT-5.6 feedback/remedial Structured Output contracts with no model tools and a deterministic Demo evaluator
- Responsive English feedback, evidence and remedial screens using flat solid backgrounds
- Exactly-one Adaptive Planning Agent decisions from validated `LearningEvidence` only
- Eight-action bounded enum with server-validated targets, tools, prerequisites and state transitions
- Penalty-free user override with only valid alternatives and no hidden reasoning display
- Prerequisite/review detours that return to the interrupted concept after mastery
- Named-gap validation and `request_search` gating that stops before any external request
- Strict real GPT-5.6 function calling with one forced tool call, disabled parallel calls and a deterministic Demo policy
- Durable `agent_decision`, `search_confirmation` and `session_summary` transitions with pause/refresh recovery
- Responsive English Agent screen with one visually dominant recommendation and flat solid backgrounds

## Next action

Implement Milestone 6 controlled external search. It must require a validated named gap, session permission, an Agent `request_search` action and a separate user confirmation before any web-search tool can run.
