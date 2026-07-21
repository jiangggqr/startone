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
- Milestone 3 production focus-session shell: in progress
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

## Next action

Implement Milestone 3 focus-session shell, server-backed start-action draft, pause/resume overlay, timer preference and responsive learning workspace.
