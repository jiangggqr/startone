# StartFrame Agent

StartFrame Agent turns a learner's own PDFs, Markdown notes, text files, or pasted material into one grounded next step at a time. It combines a contextual Tutor and Guided Mastery Loop with a bounded Adaptive Planning Agent, while keeping uploaded material primary and external search under explicit learner control.

Built for the **Education** track of OpenAI Build Week with Codex and GPT-5.6.

## Judge path

The deterministic **Demo mode** is the fastest path and requires no account, API key, or internet access.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000`, select **Upload material and start a session**, and then select **Load standard Demo**. A complete judge walkthrough, including the four-gate controlled-search scenario, is in [`submission/JUDGE_TESTING_GUIDE.md`](submission/JUDGE_TESTING_GUIDE.md).

- Public Demo: pending final deployment
- API health: `/api/health`
- Interactive API schema: `/api/docs`
- Codex `/feedback` Session ID: `019f7ff7-6b6a-74d1-98b2-2f895e28bbce`

## Product boundary

1. Uploaded material is the default primary learning source.
2. StartFrame preserves real source locations and creates a verifiable knowledge map, a 2–5 concept route, and one 60–120 second start action.
3. Tutor explains, asks questions, and guides only the active concept.
4. Tutor, Quiz, free recall, progressive hints, immediate feedback, specific encouragement, and remedial practice form the Guided Mastery Loop.
5. The loop produces factual `LearningEvidence` with no recommendation fields.
6. The Adaptive Planning Agent reads validated evidence and selects exactly one bounded global action. It does not teach or score.
7. External search can execute only when the session permits suggestions, the server validates a named `SourceGap`, the Agent selects `request_search`, and the learner confirms that exact scope.

The product is ADHD-informed, but it makes no medical, diagnostic, or treatment claims.

## What works

- PDF, Markdown, TXT, and pasted-text ingestion with page, heading, line, paragraph, and character locations
- Stable chunks, checksums, source preview, parsing progress, partial success, retry, cancellation, deletion, and location reports
- Source coverage, named gaps, dependency map, adjustable route, and short start action
- One-active-concept focus workspace with optional timer, autosave, optimistic conflict resolution, pause, exact resume, and concrete restart action
- Source-grounded Tutor with six quick supports, free questions, a guidance ladder, persistent conversation, and factual confusion signals
- One-question Quiz, misconception-based distractors, free recall, and three progressive hint levels
- Five-part feedback, specific encouragement, targeted remediation, and recommendation-free evidence
- Eight bounded Agent actions, one visible recommendation, server-valid alternatives, penalty-free override, and prerequisite/review return paths
- Four server-revalidated search gates, required real-mode web search, citation-only persistence, and uploaded-source primacy after selection
- A visibly separate topic-only AI-supplement fallback
- Searchable session history, safe copy/delete, JSON/Markdown export, AI activity history, accessibility preferences, and full workspace deletion
- Anonymous workspace isolation, private UUID file storage, public-release quotas, hardened browser headers, and no-store API responses
- English-only production UI, flat solid backgrounds, visible focus, semantic controls, and responsive desktop/tablet/390 px flows

## GPT-5.6 implementation

Real mode calls the OpenAI Responses API only from the FastAPI server. GPT-5.6 is used for:

- source coverage, knowledge-map creation, and the short start action;
- contextual Tutor guidance;
- Quiz and recall generation;
- structured feedback and targeted remediation;
- exactly-one Adaptive Planning Agent decision; and
- controlled external search after all four gates pass.

UI-facing model outputs use strict Pydantic Structured Outputs. Every model-provided source reference is validated against workspace, session, source, and chunk ownership before persistence or rendering. The Agent uses one forced strict function call with parallel calls disabled. The search execution path exposes only `web_search`, requires it for that request, and persists only cited public HTTPS URLs.

Demo and real modes are deliberately separate. Demo output is deterministic and visibly labeled. Real-mode failures never silently fall back to fixtures.

## How Codex was used

The repository began with a Chinese product specification, a 22-screen clickable low-fidelity prototype, sample materials, and 42 acceptance cases—no application code. In one primary Codex task, the project was implemented milestone by milestone with a focused commit after each verified stage.

Codex accelerated the FastAPI/SQLite foundation, grounded parsers, schema and state-machine implementation, strict AI contracts, static responsive interface, automated tests, security audit, and repeated browser verification. Human decisions defined and protected the important boundaries: source priority, Tutor versus Agent responsibility, observation-only evidence, the four-gate search policy, anonymous privacy model, English-only UI, and flat visual style.

Browser QA drove concrete corrections, including stable Tutor message ordering, mobile header reflow, source-origin preservation, a fully functional topic-only fallback, location reporting, and history/data controls. See [`CODEX_BUILD_LOG.md`](CODEX_BUILD_LOG.md) for dated milestones, tests, corrections, and commits.

## Run and test

Python 3.11 or newer is required. Python 3.13 is used by CI and the deployment image.

```bash
source .venv/bin/activate
python -m pytest -q
python -m pip check
```

The no-key Demo uses the files in `sample_data/`. The current verification record maps every core and UI acceptance case in [`evals/VERIFICATION_REPORT.md`](evals/VERIFICATION_REPORT.md).

## Real mode

Configure credentials only in a local `.env` or deployment secret:

```dotenv
STARTFRAME_MODE=real
OPENAI_API_KEY=your-server-side-secret
STARTFRAME_OPENAI_MODEL=gpt-5.6
```

Never paste a key into chat, browser code, documentation, screenshots, video, logs, or Git. Without a server-side key, real mode returns an explicit recoverable error and never switches to Demo mode.

## Deployment

The repository includes a non-root Docker image and a Render Blueprint. See [`DEPLOYMENT.md`](DEPLOYMENT.md) for public Demo and private GPT-5.6 smoke-test instructions.

The default public deployment is Demo mode without an OpenAI key, which prevents anonymous visitors from spending model credits. Free-tier filesystem storage is resettable; durable production use requires persistent storage.

## Architecture

```text
Browser: static HTML/CSS/JavaScript
        │ same-origin JSON API + HTTP-only workspace cookie
        ▼
FastAPI: state validation, source ownership, quotas, AI boundaries
        ├── SQLite: sessions, sources, activities, evidence, decisions
        ├── private uploads: UUID-named immutable blobs
        └── OpenAI Responses API: real mode only, server-side key
```

```text
app/          FastAPI service, AI gateway, domain services, production UI
tests/        Unit and integration tests
docs/         Product, interaction, data, AI, and acceptance specifications
prototype/    Low-fidelity behavior/layout reference; not production code
sample_data/  Deterministic Demo learning material
evals/        Core product/UI acceptance cases and verification record
submission/   English Devpost copy, judge guide, video script, checklist
```

## Known release limitations

- The public no-key Demo is deterministic; a private server-side key is required for live GPT-5.6 verification.
- Anonymous workspaces are browser-specific and do not sync across devices.
- SQLite and local file storage are appropriate for the hackathon release, not horizontal scaling.
- Render's free filesystem is ephemeral, so judge Demo data can reset after a restart.
- Long-term spaced repetition, accounts, teacher administration, social ranking, payments, and medical claims are intentionally out of scope.

## Project references

- [`STARTFRAME_FULL_SPEC_CN.md`](STARTFRAME_FULL_SPEC_CN.md) — complete internal product specification
- [`PLANS.md`](PLANS.md) — dependency-ordered implementation record
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md) — current completion status
- [`docs/18_DECISIONS_AND_SCOPE_CN.md`](docs/18_DECISIONS_AND_SCOPE_CN.md) — binding decisions and conflict resolution
- [`prototype/startframe_lowfi_prototype.html`](prototype/startframe_lowfi_prototype.html) — clickable low-fidelity design reference

## License

MIT. See [`LICENSE`](LICENSE).
