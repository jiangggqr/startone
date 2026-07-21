# StartOne repository guidance

## Read before coding

Read `STARTFRAME_FULL_SPEC_CN.md`, `PLANS.md`, the relevant numbered files in `docs/`, and `prototype/startframe_lowfi_prototype.html` before each milestone.

## Product boundaries

- Uploaded learning material is the required primary source and the only product entry path.
- Do not gate learning behind a goal, prior-knowledge, time or energy form or a pre-test. AI proposes the learning focus and map from the material, then opens a beginner-friendly first explanation; later validated learning evidence calibrates support.
- Guided Mastery Loop teaches and evaluates the active concept.
- Adaptive Planning Agent only selects one next action from validated evidence.
- `LearningEvidence` contains observations, never recommendations.
- StartOne never searches the web. If a validated named `SourceGap` blocks learning, the Agent may select `request_more_material`, which asks the learner to upload the missing material or continue within the current scope.
- Uploaded or pasted material is the only learning source. AI may reorganize, paraphrase, question, and explain that material, but must not introduce outside facts or present generated wording as a separate source.
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
- Keep deterministic fixtures and real-model execution separate internally and in tests. Do not expose evaluator controls or a global mode badge in the learner product UI.

## Definition of done

A milestone is complete only when relevant tests pass, the changed browser flow is exercised, failures are reported honestly, documentation is updated, and a focused Git commit is created.
