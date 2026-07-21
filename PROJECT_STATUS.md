# StartOne project status

## Current state

- Product specification: complete
- UI/UX information architecture: complete
- Clickable low-fidelity prototype: complete
- Production UX and accessibility rules: complete
- Data, AI and API contracts: complete
- Acceptance scenarios and Codex prompts: complete
- Milestone 0 application foundation: complete
- Milestone 1 source ingestion and grounding: complete
- Milestone 2 automatic material analysis, coverage and knowledge map: complete
- Milestone 3 production focus-session shell: complete
- Milestone 4A contextual Tutor: complete
- Milestone 4B Quiz and free recall: complete
- Milestone 4C feedback, remediation and LearningEvidence: complete
- Milestone 5 Adaptive Planning Agent: complete
- Milestone 6 controlled external search: complete
- Milestone 7 production hardening: complete, including isolated live GPT-5.6 core-flow verification
- Milestone 8 submission readiness: local 1.0.0 release package and live smoke test complete; external publication steps pending
- Production UI language: English
- Product positioning: focus-first learning; AI and technical learning are the launch focus, but the source-grounded MVP is not restricted to one subject
- Product mechanism: the StartOne Momentum Loop — start one clear step, see the whole framework, focus on one concept, retrieve once, receive truthful feedback, and continue automatically

## What the prototype is

`prototype/startframe_lowfi_prototype.html` is a self-contained clickable design artifact. It demonstrates all major screens, the main flow and representative state/recovery branches. The numbered UX specs and evals remain authoritative for the complete production state matrix. It is not the production application and should not be deployed as the final project.

## Implemented foundation

- Python 3.11+ FastAPI/Uvicorn service and versioned SQLite initialization
- Static responsive application shell with accessible landmarks, controls and dialog
- Internal runtime health reporting through `GET /api/health`; no mode or evaluator controls in the learner UI
- Empty-state, offline-health and recoverable failure handling
- Automated foundation tests and real desktop/mobile browser inspection
- Anonymous workspace Cookie isolation and private UUID-based source storage
- PDF, Markdown, TXT and pasted-text parsing with real source locations
- Stable source/chunk IDs, checksums, local retrieval, retry and source deletion
- Source inventory with empty/error/partial-success/offline/recovery states; no competing full-panel preview in the upload flow
- Material-driven automatic learning focus and map with no goal, prior-knowledge, time or energy setup gate
- Grounded source coverage with candidate gaps that never authorize search
- A connected 2–5 concept visual framework followed by a direct first-concept explanation; no route-adjustment decision or pre-test gate
- Shared server-side GPT-5.6 Responses API gateway with Pydantic Structured Outputs; the interactive default is the low-latency `gpt-5.6-luna` variant
- Server validation of every generated source/chunk reference before persistence or rendering
- Internal fixture/real-model separation, AI activity metadata and recoverable no-key/model errors
- Server-versioned focus-note and activity drafts with visible save/offline/failure/conflict states; legacy start-action drafts remain API-compatible but are absent from the learner flow
- Explicit two-copy draft conflict comparison and user-selected resolution
- One-current-concept focus workspace with a clickable map, big idea, prerequisite/current/next relationship, key parts, concrete example, memory anchor and lightweight inline citations
- Pause/resume mutation lock and refresh-safe restoration without a separate Session status rail
- Desktop two-column framework-and-lesson layout, tablet reflow and 390 px mobile session navigation
- Saved-exit summary with a concrete next restart action
- Current-concept Tutor with persisted per-concept conversation and retry-safe unsent drafts
- Six concrete Tutor quick actions, free questions and a visible seven-level guidance ladder
- Strict typed Tutor responses with validated source references and explicit uploaded/AI-supplement labels
- Factual confusion/prerequisite signals that are visibly not Agent decisions or search requests
- Tutor pause/resume, refresh recovery, inline source context and full-screen 390 px mobile flow
- Real GPT-5.6 Tutor contract path with no tools exposed; deterministic Tutor remains test-only
- Three-question concept Quiz covering definition, mechanism and application, with server-only answer keys and misconception-based distractors
- Free recall with server-only key points, acceptable paraphrases and misconception patterns
- Progressive 0–3 hint disclosure with saved depth, answer autosave and explicit conflict recovery; only requested hints are rendered
- Persistent activity attempts with source references, pause/refresh recovery and no premature evidence or Agent decision
- Strict GPT-5.6 Quiz/recall Structured Output contracts with deterministic test activities
- Full-screen practice flows with English-only copy, flat backgrounds, one centered task and no repeated source-location or system-boundary panels
- Backend five-part feedback compressed in the learner UI to correct/not-quite, answer review, one concise rationale and Keep going
- Server-validated factual `LearningEvidence` for Quiz, recall, remedial and Tutor-close boundaries with no recommendation columns
- Targeted remedial practice with five bounded strategy types and no immediate strategy repetition after an unsuccessful result
- Durable `feedback_shown`, `remedial_practice` and `evidence_ready` states with pause/refresh recovery
- Strict GPT-5.6 feedback/remedial Structured Output contracts with no model tools and a deterministic test evaluator
- Recommendation-free evidence stays internal; the learner is not asked to review or approve the evidence boundary
- Exactly-one Adaptive Planning Agent decisions from validated `LearningEvidence` only
- Eight-action bounded enum with server-validated targets, tools, prerequisites and state transitions
- Server-validated action execution with no hidden reasoning display or learner-facing alternative-path form
- Prerequisite/review detours that return to the interrupted concept after mastery
- Named-gap validation and `request_search` gating that stops before any external request
- Strict real GPT-5.6 function calling with one forced tool call, disabled parallel calls and a deterministic test policy
- Durable `agent_decision`, `search_confirmation` and `session_summary` transitions with pause/refresh recovery
- Safe Agent actions apply automatically after Keep going; there is no ordinary next-step decision screen, and evidence/Agent architecture are not exposed as learning content
- A separate search confirmation that visibly proves all four gates and states that no search has run before confirmation
- Execution-time revalidation of session permission, named gap, accepted Agent request and exact-scope user confirmation
- Required real-mode Responses API web search with cited public HTTPS result filtering and server-only credentials
- Deterministic search results and a controlled-search one-source fixture for internal testing only
- Canonical URL, publisher, access time, cited summary, selection reason and `external` origin on every result
- One-source selection or penalty-free ignore, with uploaded material retained as the primary source
- Durable search confirmation, running, result, failure, cancel and focus-return recovery states
- Searchable/filterable learning history, session copy/delete, JSON/Markdown export, AI activity log and full workspace deletion
- Saved larger-text, reduced-motion and search-suggestion preferences
- Exact source-location validation and lightweight learner-facing citations without learning-progress side effects
- API no-store policy and hardened CSP, frame, MIME, referrer, permissions and opener headers
- Schema-preserving migration from uploaded-only source origins and a complete automated regression suite
- Upload-flow refinement keeps file status and the next learning action inside the primary upload panel; the homepage no longer exposes administrative/system-boundary cards
- Uploaded files and their status remain inside the upload panel; the next action builds the learning focus and map directly
- Knowledge map, source-grounded explanation, Tutor, Quiz and free recall are visible in the primary post-upload flow
- Long-source analysis samples representative excerpts across the entire document, reports coverage and route-building as separate visible stages, caps a failed model attempt at one request, and resumes from any completed stage
- Model timeout, connection, authentication, access, rate-limit and invalid-request failures use distinct recoverable messages; interrupted operations are closed on server restart instead of remaining stuck as running
- Model-facing citations use short aliases that are mapped back to real source/chunk IDs and revalidated before persistence; impossible generated prerequisite links are removed deterministically before the full map integrity check
- Homepage value proposition now leads with fast initiation, a coherent knowledge structure, sustained concept-by-concept progress and learning completion; material upload is the mechanism, not the product promise
- Explanation-first flow removes the suggested-outcome card, duplicate recommended-route card, route-adjustment controls, the pre-learning response test and the full-panel source preview; one click from the knowledge framework now opens the first concept lesson
- Quiz refinement removes repeated uploaded-file rows, practice-boundary copy, locked-hint cards and hint-success banners; post-answer feedback now follows a familiar result, answer and explanation pattern
- Knowledge framework nodes are keyboard-operable and reveal each concept's definition, role and dependencies without bypassing the current route
- The focus workspace is now a two-column knowledge-framework/lesson layout; the Session status rail and Agent alternative-path form are removed
- Test selection is reduced to two compact choices: 3-question multiple choice or 1-response free recall
- Keep going completes the evidence boundary, requests exactly one Agent action and applies safe actions automatically; only `request_search` stops for explicit confirmation
- Source coverage and candidate-gap validation remain server-side and no longer occupy a learner page; only a real Agent `request_search` exposes the named gap in the required confirmation view
- Session completion logic cannot end an unfinished route; a mastered final concept is marked complete before the summary is generated

## Latest verification

- 52 automated tests pass after the StartOne Momentum Loop, hidden coverage-state and automatic-continuation refinements
- JavaScript syntax, Python compilation, diff hygiene, English-only UI and no-gradient checks pass
- Browser verification created a fresh real-model session from pasted material, generated a four-node connected framework, opened the explanation, completed a real three-question Quiz, displayed a 3/3 score with one explanation per question, and automatically opened concept 2 of 4 after Keep going
- Every knowledge-framework node was exercised as a selectable explanation target without bypassing the current route
- Desktop document width matches the 1280 px viewport; there is no horizontal overflow, Chinese learner copy, gradient background, learner coverage page, Session status rail or Agent alternative-path form

## Next action

Publish the repository and server-keyed GPT-5.6 app, record/upload the under-three-minute English video, replace the three pending URLs in `submission/DEVPOST_SUBMISSION.md`, and obtain user confirmation before the final Devpost submission action.
