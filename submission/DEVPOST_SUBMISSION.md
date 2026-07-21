# Devpost submission copy

## Project name

StartFrame Agent

## Tagline

Turn your own learning materials into one grounded next step at a time.

## Category

Education

## Short description

StartFrame Agent turns a learner's PDFs, Markdown notes, text files, or pasted material into a source-verifiable knowledge map and a low-friction learning session. A contextual Tutor and Guided Mastery Loop teach and assess one active concept. Factual learning evidence then lets a bounded planning Agent select exactly one next action. External search is unavailable until four independent gates are satisfied.

## Inspiration

Many learning tools assume that the learner has already started: they wait for a good question, a clean plan, and enough working memory to decide what to do next. The harder moment is often earlier. A learner already has course material and a goal but cannot turn them into a manageable first action or tell whether understanding is improving.

StartFrame Agent was designed around that initiation-to-mastery gap. It is ADHD-informed without making medical, diagnostic, or treatment claims.

## What it does

- Treats uploaded material as the primary learning source and preserves real page, heading, line, paragraph, and character locations.
- Builds source coverage, named gaps, a compact dependency map, a 2–5 concept route, and one 60–120 second start action.
- Keeps one active concept and one visually dominant recommended action in a responsive focus workspace.
- Uses a contextual Tutor for explanation, questions, and guided checks inside the current concept.
- Runs Quiz, free recall, three-level hints, immediate feedback, specific encouragement, and targeted remediation as one Guided Mastery Loop.
- Stores `LearningEvidence` as factual observations only, with no recommendation fields.
- Lets a bounded Adaptive Planning Agent select exactly one of eight server-validated global actions from that evidence.
- Requires four gates before external search: session permission, a validated named source gap, an accepted Agent `request_search` action, and explicit confirmation of the exact scope.
- Supports autosave, optimistic conflict resolution, pause/resume, precise restart actions, exports, AI activity history, source reports, and deletion controls.

## How we built it

The app uses Python 3.11+, FastAPI, Uvicorn, SQLite, and dependency-free static HTML/CSS/JavaScript. OpenAI calls stay on the server.

Real mode uses GPT-5.6 through the Responses API for source coverage, the knowledge map and start action, Tutor guidance, Quiz and recall generation, structured feedback, remediation, and the final bounded planning decision. Fixed UI-facing model results use schema-validated Pydantic Structured Outputs. The Agent uses one forced strict function call with parallel calls disabled. The search execution endpoint exposes only `web_search`, requires it for that call, and persists only cited public HTTPS results after all four gates are revalidated.

An isolated release smoke test completed a real GPT-5.6 flow across source coverage, knowledge-map generation, Tutor, Quiz, structured feedback, and the bounded Agent. The public judge deployment intentionally stays in no-key Demo mode so anonymous visitors cannot spend model credits.

Deterministic Demo mode is a separate, visibly labeled judge path. It does not require a key or internet access and never presents fixture output as a live model response.

## How we used Codex

Codex turned a detailed Chinese product specification, a 22-screen low-fidelity prototype, and 42 acceptance cases into a dependency-ordered implementation. It accelerated schema design, source parsers, strict AI contracts, state-machine transitions, responsive UI implementation, security review, automated tests, and repeated browser verification.

The human product decisions remained explicit: uploaded-source primacy; the Tutor/Guided Mastery/Agent responsibility boundary; observation-only `LearningEvidence`; the four-gate search policy; flat, English-only UI; anonymous workspace privacy; and the choice to keep Demo and real model modes visibly separate. When browser testing exposed reversed Tutor message order, clipped mobile headers, a missing topic-only flow, and provenance relabeling risk, Codex corrected the underlying implementation and added regression coverage.

## Challenges

The hardest challenge was not generating content; it was preventing responsibilities from leaking across boundaries. Tutor had to guide without changing the route. Feedback could recommend one local micro-action but could not make a global planning decision. The Agent had to reason from validated evidence without teaching or scoring. Search had to remain technically impossible until a learner confirmed a named, evidence-backed gap.

Grounding was another challenge. Locations cannot be invented by a model, so the service creates deterministic chunks and validates every returned reference against workspace, session, source, and chunk ownership before persistence or rendering.

## Accomplishments

- A complete upload-to-summary learning loop rather than a chat-only proof of concept.
- Strict source provenance from ingestion through Tutor, activities, feedback, Agent decisions, and external supplements.
- Eight bounded Agent actions with controlled transitions and penalty-free override.
- Search that is structurally gated rather than governed by prompt wording alone.
- Exact pause, refresh, draft-conflict, and activity recovery across desktop and mobile.
- English-only production UI with flat solid backgrounds, semantic controls, visible focus, and 390 px coverage.
- A deterministic judge path plus isolated real GPT-5.6 contracts.

## What we learned

Trustworthy educational AI benefits from smaller interfaces between capabilities. Structured Outputs help with shape, but server-side source validation, state validation, tool restriction, and provenance labeling are what turn a model response into a reliable product behavior. We also learned that recovery is part of the core learning experience: preserving an unfinished sentence and returning to one concrete restart action can matter as much as the generated explanation.

## What's next

The hackathon release uses anonymous workspaces and SQLite. A post-hackathon version would add opt-in accounts, durable managed storage, user-controlled retention periods, richer document formats, longitudinal review scheduling, educator-authored source packs, and privacy-preserving product analytics. The core boundaries will remain unchanged.

## Testing instructions

Use the no-key public Demo and follow `submission/JUDGE_TESTING_GUIDE.md`. No account is required. The Demo uses resettable anonymous data and remains visibly labeled.

## Required links and identifiers

- Public Demo: `PUBLIC_DEMO_URL_PENDING`
- Code repository: `REPOSITORY_URL_PENDING`
- Public YouTube demo: `YOUTUBE_URL_PENDING`
- Codex `/feedback` Session ID: `019f7ff7-6b6a-74d1-98b2-2f895e28bbce`
