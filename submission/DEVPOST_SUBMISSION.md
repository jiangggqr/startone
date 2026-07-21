# Devpost submission copy

## Project name

StartOne

## Tagline

Start with one clear step. Keep going until it sticks.

## Category

Education

## Short description

StartOne helps learners overcome the gap between intending to learn and actually finishing. It turns source material into a visual, verifiable knowledge structure, starts with one low-friction action, teaches and checks one active concept at a time, and automatically carries factual learning evidence into the next safe step. It is built first for dense AI and technical learning, while the method works across text-based subjects.

## Inspiration

Many learning tools assume that the learner has already started: they wait for a good question, a clean plan, and enough working memory to decide what to do next. The harder problem spans the whole journey: starting despite friction, seeing how ideas connect, returning after attention breaks, and knowing whether the learning is actually complete.

StartOne was designed around that initiation-to-mastery gap. It is ADHD-informed without making medical, diagnostic, or treatment claims.

## What it does

- Treats uploaded material as the primary learning source and preserves real page, heading, line, paragraph, and character locations.
- Uses GPT-5.6 to select a learning focus from the material and build source coverage, named gaps, a connected 2–5 concept knowledge map, and beginner-friendly explanations with relationship diagrams, key parts, examples, and memory anchors.
- Removes the goal, prior-knowledge, time, and energy setup form as well as the pre-test; later validated practice evidence calibrates support.
- Keeps one active concept and one visually dominant action in a responsive focus workspace, reducing every lesson to understand → connect → retrieve.
- Uses a contextual Tutor for explanation, questions, and guided checks inside the current concept.
- Runs Quiz, free recall, three-level hints, immediate feedback, specific encouragement, and targeted remediation as one Guided Mastery Loop.
- Stores `LearningEvidence` as factual observations only, with no recommendation fields.
- Lets a bounded Adaptive Planning Agent select exactly one of eight server-validated global actions from that evidence and automatically applies safe actions so the learner does not face another planning decision.
- Requires four gates before external search: session permission, a validated named source gap, an accepted Agent `request_search` action, and explicit confirmation of the exact scope.
- Supports autosave, optimistic conflict resolution, pause/resume, precise restart actions, exports, AI activity history, lightweight inline citations, and deletion controls.

## How we built it

The app uses Python 3.11+, FastAPI, Uvicorn, SQLite, and dependency-free static HTML/CSS/JavaScript. OpenAI calls stay on the server.

Real mode uses GPT-5.6 through the Responses API for source coverage, the knowledge map and concept explanations, Tutor guidance, Quiz and recall generation, structured feedback, remediation, and the final bounded planning decision. Fixed UI-facing model results use schema-validated Pydantic Structured Outputs. The Agent uses one forced strict function call with parallel calls disabled. The search execution endpoint exposes only `web_search`, requires it for that call, and persists only cited public HTTPS results after all four gates are revalidated.

An isolated release smoke test completed a real GPT-5.6 flow across source coverage, knowledge-map generation, Tutor, Quiz, structured feedback, and the bounded Agent. The public app uses the same server-side real-model path with workspace quotas and deployment-side budget controls. Deterministic fixtures remain isolated to automated tests and are never presented as learner-selected modes.

## Built with

- Codex
- GPT-5.6
- OpenAI Responses API
- Structured Outputs and bounded function calling
- `web_search`
- Python, FastAPI, and Uvicorn
- SQLite
- HTML, CSS, and JavaScript
- Docker and Render

## How we used Codex

Codex turned a detailed Chinese product specification, a 17-view historical low-fidelity prototype, and 42 acceptance cases into a dependency-ordered implementation. It accelerated schema design, source parsers, strict AI contracts, state-machine transitions, responsive UI implementation, security review, automated tests, and repeated browser verification.

The human product decisions remained explicit: uploaded-source primacy; AI-selected learning focus without an upfront setup form; the Tutor/Guided Mastery/Agent responsibility boundary; observation-only `LearningEvidence`; the four-gate search policy; flat, English-only UI; and anonymous workspace privacy. When browser testing exposed reversed Tutor message order, clipped mobile headers, hidden learning features, unnecessary evaluator UI, and provenance relabeling risk, Codex corrected the implementation and added regression coverage.

## Challenges

The hardest challenge was not generating content; it was preventing responsibilities from leaking across boundaries. Tutor had to guide without changing the route. Feedback could recommend one local micro-action but could not make a global planning decision. The Agent had to reason from validated evidence without teaching or scoring. Search had to remain technically impossible until a learner confirmed a named, evidence-backed gap.

Grounding was another challenge. Locations cannot be invented by a model, so the service creates deterministic chunks and validates every returned reference against workspace, session, source, and chunk ownership before persistence or rendering.

## Accomplishments

- A complete StartOne Momentum Loop from one-click preparation through visual orientation, active retrieval, truthful small-win feedback and automatic safe continuation.
- Strict source provenance from ingestion through Tutor, activities, feedback, Agent decisions, and external supplements.
- Eight bounded Agent actions with controlled transitions and automatic safe continuation without another learner decision page.
- Search that is structurally gated rather than governed by prompt wording alone.
- Exact pause, refresh, draft-conflict, and activity recovery across desktop and mobile.
- English-only production UI with flat solid backgrounds, semantic controls, visible focus, and 390 px coverage.
- A real GPT-5.6 product path plus isolated deterministic regression fixtures.

## What we learned

Trustworthy educational AI benefits from smaller interfaces between capabilities. Structured Outputs help with shape, but server-side source validation, state validation, tool restriction, and provenance labeling are what turn a model response into a reliable product behavior. We also learned that recovery is part of the core learning experience: returning to one concrete restart action can matter as much as the generated explanation.

## What's next

The hackathon release uses anonymous workspaces and SQLite. A post-hackathon version would add opt-in accounts, durable managed storage, user-controlled retention periods, richer document formats, longitudinal review scheduling, educator-authored source packs, and privacy-preserving product analytics. The core boundaries will remain unchanged.

## Testing instructions

Use the public app and follow `submission/JUDGE_TESTING_GUIDE.md`. No learner account is required; the server-side GPT-5.6 credential is never exposed to the browser. Anonymous learning data is resettable.

## Required links and identifiers

- Public app: `PUBLIC_DEMO_URL_PENDING`
- Code repository: `REPOSITORY_URL_PENDING`
- Public YouTube demo: `YOUTUBE_URL_PENDING`
- Codex `/feedback` Session ID: `019f7ff7-6b6a-74d1-98b2-2f895e28bbce`
