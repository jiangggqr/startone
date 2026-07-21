# StartFrame Agent

StartFrame Agent is a source-grounded learning Web App built with FastAPI, SQLite, static HTML/CSS/JavaScript, and the OpenAI Responses API. The repository includes the complete product specification, UI/UX prototype, acceptance requirements, and an application being delivered in dependency order.

## Product model

1. The learner uploads PDF, Markdown, TXT, or pasted text as the primary learning source.
2. StartFrame preserves real page, heading, line, paragraph, and character locations, then builds a verifiable knowledge map.
3. An ADHD-informed session begins with one 60–120 second action and keeps one active concept and one dominant action visible.
4. Contextual Tutor, Quiz, free recall, progressive hints, immediate feedback, encouragement, and remedial practice form the Guided Mastery Loop.
5. The loop produces factual `LearningEvidence` with no recommendation fields.
6. The Adaptive Planning Agent reads validated evidence and selects exactly one global next action. It does not teach or score.
7. External search is available only when the session permits suggestions, a named source gap is validated, the Agent requests search, and the learner confirms that specific scope.

## Start here

1. `START_HERE_CN.md`
2. `AGENTS.md`
3. `STARTFRAME_FULL_SPEC_CN.md`
4. `prototype/startframe_lowfi_prototype.html`
5. `docs/04_LOW_FIDELITY_PROTOTYPE_CN.md`
6. `docs/16_CODEX_PROMPTS_CN.md`

The Chinese files are internal product and implementation specifications. All production UI, generated learning content, README content, submission copy, and demo narration are English.

## UI/UX reference

- Clickable prototype: `prototype/startframe_lowfi_prototype.html`
- Full prototype board: `prototype/startframe_lowfi_overview.png`
- Screen specification: `docs/05_SCREEN_AND_INTERACTION_SPEC_CN.md`
- Component and state matrix: `docs/06_COMPONENTS_AND_STATES_CN.md`
- Production UX requirements: `docs/11_PRODUCTION_UX_STANDARDS_CN.md`

The prototype is a behavior and layout reference, not production application code.

## Implemented through Milestone 4B

- Python 3.11+ FastAPI/Uvicorn service and versioned SQLite schema
- Anonymous workspace Cookie isolation and private UUID-based upload storage
- PDF, Markdown, TXT, and pasted-text ingestion with real source locations
- Stable source/chunk identifiers, checksums, retry, removal, preview, and local retrieval
- English learner setup with local recovery and optimistic server versioning
- Grounded source coverage, named candidate gaps, a 2–5 concept map, and an adjustable route
- One 60–120 second start action with a durable response draft
- One-active-concept focus workspace with an optional timer, pause/resume, and exact restart point
- Explicit two-copy conflict resolution that never silently overwrites learner input
- Per-concept Contextual Tutor conversation with six quick supports, free questions, and a seven-level guidance ladder
- Uploaded-material and AI-supplement origin labels with server-validated source references
- One-question Quiz with misconception-based distractors and a server-only answer key
- Free recall with server-only evaluation key points, paraphrases, and misconception patterns
- Three progressive hint levels, activity-linked drafts, refresh/pause recovery, and persisted attempts
- A shared server-side GPT-5.6 Responses API gateway with strict Pydantic Structured Outputs
- Clearly separated deterministic Demo mode and real-model mode
- Responsive desktop/tablet/mobile layouts, accessible semantic controls, and flat solid backgrounds

Quiz and recall submission currently records the raw attempt, hint depth, and time without creating evidence or an Agent decision. Immediate structured feedback, encouragement, remediation, and normalized `LearningEvidence` are the active Milestone 4C work. Adaptive Agent decisions and controlled external search follow in Milestones 5 and 6.

## Run locally

Python 3.11 or newer is required.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000`. API documentation is available at `http://127.0.0.1:8000/api/docs`.

Run the automated suite:

```bash
source .venv/bin/activate
python -m pytest
```

## Demo and real GPT-5.6 modes

The default `demo` mode is deterministic, visibly labeled, and needs no API key. It never presents fixed fixtures as live model results.

Real GPT-5.6 mode reads credentials only from the server environment:

```dotenv
STARTFRAME_MODE=real
OPENAI_API_KEY=your-server-side-secret
STARTFRAME_OPENAI_MODEL=gpt-5.6
```

Never paste an API key into chat, client code, documentation, logs, or Git. Without a server-side key, real mode returns an explicit recoverable error and never silently falls back to Demo mode.

## Repository layout

```text
app/                    FastAPI service and static production UI
tests/                  Automated unit and integration tests
docs/                   Product, interaction, data, and acceptance specifications
prototype/              Low-fidelity behavior and layout reference
sample_data/            Deterministic Demo learning materials
evals/                  Core product and UI/UX evaluation cases
```

See `PLANS.md` for the development sequence, `PROJECT_STATUS.md` for current progress, `CODEX_BUILD_LOG.md` for verified milestones, and `docs/18_DECISIONS_AND_SCOPE_CN.md` for binding product decisions.
