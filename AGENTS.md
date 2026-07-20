# StartFrame Agent repository guidance

## Read before coding

Read `STARTFRAME_FULL_SPEC_CN.md`, `PLANS.md`, the relevant numbered files in `docs/`, and `prototype/startframe_lowfi_prototype.html` before each milestone.

## Product boundaries

- Uploaded learning material is the default primary source.
- Guided Mastery Loop teaches and evaluates the active concept.
- Adaptive Planning Agent only selects one next action from validated evidence.
- `LearningEvidence` contains observations, never recommendations.
- External search requires all four gates: session permission, a validated named source gap, an Agent `request_search` decision, and explicit confirmation for that search.
- Always display source origin: uploaded, external supplement, or AI supplemental explanation.
- Do not make medical, diagnostic or treatment claims about ADHD.

## UX requirements

- One active concept and one visually dominant recommended action.
- Autosave, resume, pause without penalty, and a concrete next restart action.
- Implement loading, empty, error, partial-success, offline and recovery states.
- Meet WCAG 2.2 AA intent: keyboard operation, visible focus, semantic controls, non-color-only meaning, and accessible dialogs.
- Follow the responsive rules in `docs/12_ACCESSIBILITY_RESPONSIVE_CN.md`.
- Treat the prototype HTML as behavior and layout reference, not production code to copy.

## Engineering constraints

- Python 3.11+, FastAPI, Uvicorn, SQLite.
- Static HTML/CSS/JS is preferred; do not introduce a Node build system unless a documented decision changes this.
- OpenAI API calls stay on the server. Never expose keys in client code or commits.
- Use Responses API, schema-validated Structured Outputs and bounded tool/function calls.
- Keep deterministic Demo mode and real-model mode separate and visibly labeled.

## Definition of done

A milestone is complete only when relevant tests pass, the changed browser flow is exercised, failures are reported honestly, documentation is updated, and a focused Git commit is created.
