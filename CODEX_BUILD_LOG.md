# Codex build log

Record one section after each verified milestone.

## Specification and prototype baseline

- Status: complete
- Application code: not started
- Date: 2026-07-20
- Baseline commit: `specification and UX prototype baseline` (this baseline commit)
- Main Codex thread/session: current StartFrame Agent task
- Decisions resolved: four search gates; Evidence-only learning judgment; local vs global next action; anonymous workspace isolation; file storage/delete/export; source location schemes; pause/conflict recovery; normal/search Demo fixtures; Milestone 2 real-model entry
- Competition verification: OpenAI Build Week homepage and Official Rules reviewed
- Verification: 18 numbered specs present; 22 prototype screens; navigation targets valid; prototype JavaScript parses; manifest hashes regenerated

## Milestone 0 — Runnable foundation

- Status: complete
- Date: 2026-07-20
- Codex thread/session: current StartFrame Agent task
- Git commit: `54258dd`
- Goal: create a runnable, testable foundation without uploads or model calls
- Codex contribution: implemented FastAPI entry point, environment settings, SQLite schema initialization, security headers, health endpoint, static responsive shell and automated tests
- Human product decision: all user-visible product content must be English; Chinese remains internal specification language only
- Files changed: `app/`, `tests/`, `requirements.txt`, `.env.example`, `README.md`, project status and decision records
- Verification: Python 3.13 virtual environment; 2 automated tests passed; Python and JavaScript syntax passed; desktop and 390 px responsive layouts inspected in the in-app browser; primary dialog exercised; browser console reported zero errors; application source scanned for Chinese UI text with no matches
- Problems and corrections: default Python was 3.9, so the existing Python 3.13 runtime was used; port 8000 was occupied by another local project, so browser verification used port 8010 while the documented/default StartFrame port remains 8000; the first UI draft was Chinese and was corrected immediately to English across UI, runtime states, tests and the governing decision record
- Remaining limitations: upload and learning workflows intentionally begin in Milestone 1; no OpenAI call exists in this milestone

## Milestone template

### Date and milestone
- Date:
- Milestone:
- Codex thread/session:
- Git commit:

### Goal

### Codex contribution

### Human product decisions

### Files changed

### Verification results

### Problems and corrections

### Remaining limitations

## Milestone 1 — Source ingestion and grounding

- Status: complete
- Date: 2026-07-20
- Codex thread/session: current StartFrame Agent task
- Git commit: `04447e6`
- Goal: accept PDF, Markdown, TXT and pasted text while preserving real, server-validated locations
- Codex contribution: added anonymous workspace isolation, version-2 SQLite source schema, UUID/checksum blob storage, structural parsers, stable chunk IDs, local source retrieval, source APIs, retry/cancel/delete behaviors, an English upload inventory and a verifiable preview UI
- Human product decisions: every user-visible product string is English; the visual system uses flat backgrounds and does not use large-area gradients
- Files changed: source/config/database/API modules, static app, source tests, environment and dependency declarations, status and decision records
- Verification: 9 automated tests passed; Markdown heading/line locators, PDF page locators, scanned-PDF failure, pasted paragraph locators, partial multi-file success, stable retry IDs, local retrieval, workspace isolation and blob cleanup were exercised; Python and JavaScript syntax passed; app source contained no Chinese UI strings or gradient declarations
- Browser verification: real pasted-text creation → parsing → inventory → two-paragraph preview passed; delete-confirmation cancel returned focus to the Remove trigger; 390 px viewport had 390 px document width with no horizontal overflow; browser console reported zero errors
- Problems and corrections: the in-app browser does not support automated native file selection, so PDF/Markdown/TXT multipart upload is covered by API integration tests while the complete pasted-source UI path is covered in-browser; stale Milestone 0 data copy and an overly prominent disabled future action were corrected
- Remaining limitations: source coverage and session setup begin in Milestone 2; no OpenAI call exists in Milestone 1; the current environment does not yet contain `OPENAI_API_KEY`

## Milestone 2 — Learner setup, coverage and knowledge map

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: `c2b2304`
- Goal: turn ready uploaded sources into an English session setup, grounded coverage review, 2–5 concept map, adjustable route and one 60–120 second start action
- Codex contribution: added schema version 3, optimistic setup persistence, candidate SourceGap records, typed coverage/map schemas, a shared server-side Responses API gateway, deterministic Demo generation, real GPT-5.6 configuration, source-reference validation, AI activity metadata, Demo material loading and the complete pre-learning browser flow
- Human product decisions: the production UI and generated learning content stay in English; all major backgrounds are flat colors; the OpenAI key is configured only in local/deployment environment variables and is never pasted into chat or committed
- Files changed: AI and learning modules, settings, database migration, API routes, static UI, tests, environment template, dependency list and milestone records
- Verification: 14 automated tests passed; OpenAI SDK 2.46.0 generated strict response formats for both Pydantic output types; Demo setup → coverage → map → route adjustment → confirmation passed; real mode without a key returned an explicit recoverable error; invalid model source references were rejected before persistence; malformed setup requests used the product error envelope
- Browser verification: loaded both real Demo Markdown sources, reviewed exact heading/line citations, saved English setup, generated coverage and a five-concept route, shortened/restored/confirmed the route, saved/restored the first-action draft, opened a source from the map and returned focus to the exact trigger; 390 px viewport had 390 px document width with no horizontal overflow; browser console reported zero errors; visual inspection confirmed solid backgrounds and no large-area gradients
- Official API alignment: implementation uses the Responses API `responses.parse` path, `gpt-5.6` server default, low reasoning effort, `store=False`, a privacy-preserving safety identifier and Pydantic Structured Outputs; the OpenAI SDK was inspected locally to confirm these parameters
- Problems and corrections: local ports 8000 and 8010 were already occupied, so browser verification used 8020; a source-reference preview initially lacked a direct return path, so it now returns to coverage/map and restores focus to the invoking citation control
- Remaining limitations: the environment has no `OPENAI_API_KEY`, so the live GPT-5.6 smoke test is deferred to final hardening; the start-action answer is currently restored from local storage and becomes a versioned server draft in Milestone 3; no external search tool is exposed in this milestone

## Milestone 3 — Production focus-session shell

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: `7d3b1b0`
- Goal: make the first learning step durable, resumable and usable across desktop, tablet and mobile without adding Tutor or mastery judgments early
- Codex contribution: added schema version 4; server-versioned drafts; explicit two-copy conflict resolution; start-action completion; one-active-concept initialization; source-backed focus payloads; elapsed/remaining timer state; pause/resume mutation locks; a responsive three-column focus workspace; 390 px bottom session navigation; offline/save status; source-return focus restoration; and a concrete restart summary
- Human product decisions: the Demo route treats Transformer goal as completed orientation and starts active learning at Self-attention; a focus note is an ungraded navigation aid and never LearningEvidence; all user-visible copy remains English and all large backgrounds remain flat colors
- Files changed: focus-state service, schema/API/session serialization, static focus/start/summary UI, automated tests, project status and milestone records
- Verification: 17 automated tests passed; Python compilation, JavaScript syntax and diff hygiene passed; application/test/environment files contained no Chinese UI strings or gradient declarations
- Browser verification: created a new grounded session; completed and server-autosaved the 90-second start answer; entered Self-attention as the only active concept; opened the exact uploaded line reference and returned keyboard focus to the invoking control; autosaved a focus note; paused with the mutation lock; resumed and refreshed with draft, concept and timer intact; saved and exited to a concrete restart action; and resolved a real two-tab draft conflict after comparing both copies
- Responsive verification: at 390 px the Map/Learn/More panels were operable from the fixed bottom navigation, the document width remained exactly 390 px with no horizontal overflow, and visual inspection confirmed solid backgrounds with no large-area gradient
- Problems and corrections: the initial test module import did not resolve under pytest collection and was converted to an explicit test package import; draft conflict QA intentionally used two live pages to prove that no copy is silently overwritten
- Remaining limitations: Tutor is deliberately disclosed as the next Guided Mastery Loop milestone; the environment still has no `OPENAI_API_KEY`, which is not needed for this deterministic milestone

## Milestone 4A — Contextual Tutor

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: `014c34b`
- Goal: add continuous, low-pressure support for the active concept without giving Tutor any planning or search authority
- Codex contribution: added schema version 5, per-concept Tutor threads, ordered persistent messages, six quick support actions, free questions, a seven-level guidance ladder, retry-safe unsent drafts, explicit uploaded/AI-supplement origins, checking questions, factual difficulty signals, bounded source retrieval, server-side source-reference validation, Demo responses and a strict GPT-5.6 Structured Output path
- Human product decisions: Tutor remains an overlay on `learning_concept`; one thread is retained per session/concept and can be closed/reopened without losing history; Tutor close records aggregate signal counts but does not create `LearningEvidence` before Milestone 4C; no Tutor request receives a search or route-change tool
- Files changed: Tutor schema/service/API, typed AI response model, focus/Tutor UI and responsive styles, automated tests, milestone/status/decision records
- Verification: 21 automated tests passed; Demo quick actions, free questions, confusion signals, covered prerequisites, AI supplemental example labels, pause locks, close/reopen persistence and optimistic thread versions passed; a fake Responses client verified `gpt-5.6`, typed `TutorResponseOutput`, `store=False` and absence of any `tools` argument; Python/JavaScript/diff checks passed; application files contained no Chinese UI strings or gradient declarations
- Browser verification: opened Tutor from the dominant focus action; ran a checking question; autosaved and submitted a free confusion message; displayed a factual signal with explicit non-Agent/non-search wording; generated an AI supplemental example with its correct source label; opened an exact source and returned focus to the invoking citation; paused/resumed the same conversation; closed Tutor and restored focus to its trigger
- Responsive verification: the real Tutor flow opened from the 390 px bottom navigation, document width equaled viewport width with no horizontal overflow, and visual inspection confirmed a flat-background full-screen conversation layout
- Problems and corrections: Tutor messages initially used second-resolution timestamps plus UUIDs for ordering, which could reverse a same-turn pair; reads now use SQLite insertion order; the Tutor source viewer initially displayed an incorrect “Back to library” label even though it returned correctly, and was corrected to “Back to Tutor” with focus restoration rechecked
- Remaining limitations: `LearningEvidence`, structured feedback, Quiz, recall and remediation intentionally begin in Milestones 4B/4C; the live GPT-5.6 smoke test remains pending a deployment-only API key

## Milestone 4B — Quiz and free recall

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: Milestone 4B focused commit (this commit)
- Goal: add one-question Quiz and free recall with progressive support and durable attempts while preserving the Tutor/Agent boundary
- Codex contribution: added schema version 6, typed Quiz/recall outputs, current-concept activity generation, server-only evaluation keys, misconception-based Quiz distractors, three-level hints, activity-linked drafts, versioned hint reveals, durable attempts, pause/refresh recovery, source return and responsive English practice screens
- Human product decisions: answers and scoring rubrics remain hidden until feedback; a 4B submission records facts but creates no `LearningEvidence`, Agent decision or search request; Tutor remains the dominant recommended focus action while Quiz and recall are visually secondary
- Files changed: activity schema/service/API, typed AI models, focus state support, static practice UI, automated tests, README, status and decision records
- Verification: 24 automated tests passed; Quiz answer keys, misconception tags and option explanations were absent from pre-feedback API payloads; recall key points and misconception patterns stayed server-only; activity draft conflicts, hints, pause/resume, attempts, source validation and boundary flags passed; a fake Responses client verified `gpt-5.6`, typed `QuizActivityOutput`, `store=False` and no `tools` argument; JavaScript syntax and diff hygiene passed; application/test files contained no Chinese UI strings or gradient declarations
- Browser verification: launched Quiz from the active concept, selected an answer, revealed a hint, restored the same answer and hint through a fresh page, opened the exact uploaded source and returned to practice, paused/resumed, submitted without exposing correctness, returned to the concept, then created and submitted a free recall with two progressive hints; all browser requests completed without server errors
- Responsive verification: the complete recall screen and fixed Practice navigation were exercised at 390 px; visual inspection caught a clipped header badge, the activity header was changed to a stacked mobile layout, and the corrected screen was rechecked with flat solid backgrounds and no visible critical horizontal clipping
- Problems and corrections: a stale browser-control tab stopped accepting clicks during repeated QA, so the same saved practice was reopened in a fresh tab and recovery was confirmed; the first mobile activity heading placed two non-wrapping badges in one row, which was corrected before completion
- Remaining limitations: immediate correctness/coverage feedback, encouragement, remediation and `LearningEvidence` intentionally begin in Milestone 4C; the live GPT-5.6 smoke test remains pending a deployment-only API key

## Milestone 4C — Feedback, remediation and LearningEvidence

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: Milestone 4C focused commit (this commit)
- Goal: close the Guided Mastery Loop with immediate structured feedback, specific encouragement, targeted remediation and normalized factual evidence while preserving the Agent/search boundary
- Codex contribution: added schema version 7; strict feedback and remedial output models; deterministic and real GPT-5.6 generation paths; fixed five-part feedback; Quiz/recall/remedial evaluation; misconception tags; five rotating remedial strategies; Tutor-close aggregation; recommendation-free `LearningEvidence`; durable feedback/remedial/evidence-ready states; and responsive English screens
- Human product decisions: Feedback's next micro-action remains local to the active concept; `LearningEvidence` has no recommendation fields; ungraded Tutor boundaries use `outcome=unresolved`; finishing feedback means evidence is ready, not that the Agent has already decided; no 4C operation can search
- Files changed: mastery schema/service/API, typed AI models, activity/Tutor/focus state handling, feedback/remedial/evidence UI, automated tests, README and milestone records
- Verification: 27 automated tests passed; fake Responses clients verified `gpt-5.6`, typed `FeedbackOutput` and `RemedialActivityOutput`, `store=False` and no `tools` argument; Quiz/recall/remedial evidence, Tutor-close evidence, idempotent feedback, pause locks and database column exclusions passed; Python compilation and JavaScript syntax passed
- Browser verification: restored a previously submitted recall and generated complete feedback; completed the evidence boundary; built a fresh source-grounded session; submitted a misconception-based Quiz answer; reviewed all five feedback sections and factual evidence; paused/resumed the same feedback; started, restored and completed a one-sentence remedial task; and returned to structured remedial feedback without server errors
- Responsive verification: the evidence-ready view was visually inspected at 390 px with no critical horizontal clipping; desktop feedback used a stable two-column layout with a sticky evidence panel; all backgrounds remained flat solid colors with no gradients
- Problems and corrections: browser QA found that remedial input still said “2–3 sentence explanation” and omitted its completion condition; the view now uses a one-sentence label and shows the condition. The deterministic evaluator initially reused the three-point Self-attention recall heuristic for one-point remediation; it now evaluates the remedial rubric independently
- Remaining limitations: the Adaptive Planning Agent is intentionally not created until Milestone 5; controlled external search remains unavailable until Milestone 6; the live GPT-5.6 smoke test still requires a server-side deployment key

## Milestone 5 — Adaptive Planning Agent

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: Milestone 5 focused commit (this commit)
- Goal: select and apply exactly one bounded global next action from validated evidence without letting the Agent teach, score, write arbitrary state or search
- Codex contribution: added schema version 8; the eight-action Agent enum; immutable evidence snapshots; deterministic Demo policy; strict GPT-5.6 function calling; server validation of action, target and required tool; idempotent decisions; loop guards; penalty-free override; controlled concept activation; prerequisite/review detours and returns; and durable Agent/search-confirmation/session-summary states
- Human product decisions: `LearningEvidence` is the sole source for learning-performance claims; time, energy, route, prerequisites, coverage, retry history and permission are feasibility constraints only; one recommendation is visually dominant; user overrides are recorded without penalty; `request_search` never executes search and must stop at a separate confirmation
- Files changed: Agent schema/service/API, strict AI output contract, focus-state recovery, responsive Agent UI, automated tests, README, plans, project status and build log
- Verification: 32 automated tests passed; normal progression, retry, invalid override rejection, penalty-free finish, prerequisite insertion/return, named-gap search gating, evidence-based idempotency and workspace ownership passed; a fake Responses client verified `gpt-5.6`, `store=False`, a forced named function, `parallel_tool_calls=False`, strict schema and required fields; Python compilation, JavaScript syntax, diff hygiene, English-only UI scan and no-gradient scan passed
- Browser verification: resumed a saved evidence boundary; generated one visible decision; expanded only server-valid alternatives; paused/resumed the exact Agent state; applied a penalty-free override and reached the next concept; built a fresh recall → feedback → evidence → Agent flow and accepted normal progression; accepted a retry action and automatically opened the controlled same-format practice activity
- Responsive verification: desktop Agent view showed the evidence snapshot beside one dominant action with no horizontal overflow or gradients. At 390 px, visual QA found the evidence card initially pushed the recommendation below the first viewport; the layout was corrected to place the decision first, then rechecked with a 370 px-wide primary card, no horizontal overflow and no gradients
- Problems and corrections: browser exploration found that an override reason and busy button label leaked into the next decision; Agent rendering now clears all per-decision form and busy state. The project parent folder was externally renamed during browser QA, which temporarily disconnected the running SQLite path; the exact verified folder was restored to the configured workspace name and the browser flow resumed successfully
- Remaining limitations: external search execution and its second confirmation begin in Milestone 6; the live GPT-5.6 smoke test remains pending a server-side deployment key, while its request contract is fully tested

## Milestone 6 — Controlled external search

- Status: complete
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: Milestone 6 focused commit (this commit)
- Goal: allow one bounded external supplement only after a validated material gap, Agent request and exact-scope learner confirmation, without weakening uploaded-material primacy
- Codex contribution: added schema version 9; durable search requests and external sources; four-gate creation and execution checks; confirmation, decline, cancel, failure, results, selection and ignore transitions; deterministic Demo results; real GPT-5.6 Responses API web search; citation-only public HTTPS filtering; concept-source linking; English responsive search UI; and a separately reachable controlled-search Demo fixture
- Human product decisions: the confirmation is a distinct learner action after accepting the Agent recommendation; no request runs before it; real search is forced for that one Responses call; uploaded material remains primary after an external supplement is selected; keys remain server-only and are unnecessary for Demo mode
- Files changed: search service/schema/API, focus payload, static search and source UI, Demo fixture loading, automated tests, README, plans, project status, data contract, decision record, judge path and build log
- Verification: 36 automated tests passed; execution before confirmation was rejected; decline persisted no external source; all four gates were revalidated; Demo returned three cited external records; selection attached one supplement; ignore returned without penalty; a fake Responses client verified `gpt-5.6`, required `web_search`, included tool sources, `store=False`, safety identifier and citation-only canonicalized results; Python and JavaScript syntax passed
- Browser verification: the search confirmation, pause/resume, deterministic results, external source selection and ignore flows were exercised end to end; a fresh session loaded only `transformer_notes.md` from the new controlled-search button; all visible copy was English; selected supplements were clearly separate from uploaded primary sources
- Responsive verification: confirmation and results were checked at 390 px with document width equal to viewport width and exactly one visible primary result action; the new source fixture controls also remained at 390 px without overflow; computed body background image was `none`
- Problems and corrections: the first Demo path loaded the complete matrix prerequisite and therefore could not naturally exhibit the dot-product gap; a dedicated one-source fixture was exposed in the normal UI and covered by integration and browser tests. A local Python cache location was not writable in the sandbox, so compilation was rerun with an isolated temporary cache
- Remaining limitations: the live GPT-5.6 search smoke test requires a server-side `OPENAI_API_KEY`; its exact request contract and result filtering are tested with a fake Responses client. Milestone 7 will complete cross-state accessibility, security/privacy, evaluation and deployment hardening

## Milestone 7 — End-to-end production hardening

- Status: implementation and Demo verification complete; one live smoke test remains externally gated
- Date: 2026-07-21
- Codex thread/session: current StartFrame Agent task
- Git commit: Milestone 7 focused commit (this commit)
- Goal: close cross-milestone product, state, accessibility, responsive, privacy, data-control and evaluation gaps before submission packaging
- Codex contribution: added safe session copy/delete, full learning-record exports, AI activity visibility, workspace deletion, durable summaries, a structured topic-only AI-supplement fallback, schema-preserving source-origin migration, source-location reports, history search/filter, saved accessibility/new-session preferences and hardened response headers
- Human product decisions: upload remains the primary and dominant path; topic-only is a visibly weaker fallback; every production string remains English; all major backgrounds remain flat solid colors; keys stay server-only
- Verification: 43 automated tests passed; Python compilation, dependency integrity, secret scan, diff hygiene, English UI scan and no-gradient scan passed; every C01–C22 and U01–U20 case has evidence in `evals/VERIFICATION_REPORT.md`
- Browser verification: topic-only source generation preserved `ai_supplement` through preview and coverage; source reporting bound the exact chunk and restored focus; history filtering returned an exact match count; accessibility preferences persisted; data controls and deletion dialogs were exercised; summary recovery displayed completed/remaining concepts and a concrete restart action
- Responsive verification: at 390 px, normal and large-text modes had document width equal to viewport width, no undersized visible control, no gradients and no Chinese UI; the 640 px zoom-equivalent layout preserved every core operation without overflow
- Security/privacy verification: API responses use `no-store`; browser headers deny framing and sensitive capabilities; exports exclude keys, server paths, hidden rubrics, internal prompts and response IDs; source/report/session access is workspace-scoped
- Problems and corrections: the production topic-only card was initially static and is now fully functional; AI fallback provenance initially risked being relabeled downstream and is now derived at every layer; the audit also found missing source reports, history filters and user accessibility preferences, all of which are now implemented rather than deferred
- Remaining limitation: one real GPT-5.6 smoke flow requires a server-side `OPENAI_API_KEY`; deterministic Demo and all real request contracts are already verified without exposing a secret

## Milestone 8 — Submission readiness

- Status: local release package complete; external publication gates pending
- Date: 2026-07-21
- Codex thread/session: `019f7ff7-6b6a-74d1-98b2-2f895e28bbce`
- Git commit: Milestone 8 focused commit (this commit)
- Goal: produce a judge-ready 1.0.0 release, deployment path and complete English submission package without exposing credentials or prematurely publishing the final entry
- Codex contribution: rechecked the live Devpost overview and Official Rules; added public per-workspace quotas, release metadata, non-root Docker packaging, a Render Blueprint, CI, MIT license, deployment documentation, judge instructions, full Devpost copy, a timed 2:50 video script and a final compliance checklist; also resolved the historical package-validation wording that could be mistaken for current status
- Human product decisions: the public anonymous deployment stays in visibly labeled deterministic Demo mode without an OpenAI key; the required live GPT-5.6 verification is private and server-side; final repository publication, hosting, YouTube upload and Devpost submit remain explicit user-controlled external actions
- Verification: 45 automated tests passed; dependency integrity and diff hygiene passed; Render YAML parsed; `/api/health` reported version 1.0.0 and schema 11; official requirements were verified against `openai.devpost.com` and its rules page on 2026-07-21; after a server-side key was configured, an isolated real `gpt-5.6` smoke flow passed source coverage, knowledge map, Tutor, Quiz, structured feedback and a bounded Agent decision without printing the key or generated content
- Browser verification: the release opened from a fresh request, created a session, loaded both standard Demo sources, rendered exact source locations and showed an English-only healthy Demo state; at 390 px, document width matched viewport width, no visible control was under 24×24 CSS px, body background image was `none`, and no Chinese UI string was present
- Problems and corrections: GitHub CLI was installed but its saved authentication token was invalid, so no repository was created or pushed and no URL was fabricated; Docker was unavailable locally, so the image definition is covered by source review and the app itself was smoke-tested with the same Uvicorn entry point, while final platform build remains an external deployment gate
- Remaining external gates: Git hosting publication and judge access; public HTTPS Demo; under-three-minute public YouTube video; replacement of pending URLs; user-confirmed Devpost submission before the deadline. Real web-search request shape and citation filtering remain contract-tested rather than live-run, while the required real GPT-5.6 core smoke gate is complete

## Product-flow refinement — material to visible learning

- Status: complete
- Date: 2026-07-21
- Codex thread/session: `019f7ff7-6b6a-74d1-98b2-2f895e28bbce`
- Goal: reduce decision cost and make every core learning capability visible from the primary upload flow
- Human product decisions: uploaded or pasted material is the only starting path; the learner does not fill a goal, prior-knowledge, time or energy form; AI selects a learning focus from the material but must not claim to know prior mastery; the first short response and later Tutor/Quiz/recall evidence calibrate support; evaluator controls and runtime badges do not belong in the learner UI
- Codex contribution: removed the topic-only feature, setup screen and public setup endpoint; added one automatic material-to-coverage/map endpoint; placed uploaded file status and the dominant next action inside the upload panel; surfaced the AI-selected focus, knowledge framework, concept explanation, Tutor, Quiz and free recall in one direct route; moved optional data/preferences to Settings; removed global mode/model labels and evaluator shortcuts; aligned the specifications, prototype, deployment guide and submission copy
- Verification: 43 automated tests passed; Python compilation, JavaScript syntax, dependency integrity and diff hygiene passed; the browser completed upload → automatic map → starting response → explanation → Tutor → Quiz → free recall; at 390 px document width matched viewport width, the body background image was `none`, and no Chinese UI was visible
- Recovery and trust: file status remains in the upload panel, all source references stay validated, `LearningEvidence` remains recommendation-free, the Agent remains exactly-one-action, and search still requires all four gates plus exact user confirmation

## Production correction — long-PDF learning-path latency and recovery

- Status: complete
- Date: 2026-07-21
- Trigger: a real 49-page, 72-chunk PDF stayed on “Analyzing your material…” for about 91 seconds, then displayed a generic connection error
- Root cause: the synchronous request used the quality-first `gpt-5.6` alias with low reasoning effort, one SDK retry doubled the visible timeout, long-source context stopped at the first character budget instead of sampling the whole document, and the UI exposed no stage boundary
- Correction: use the low-latency GPT-5.6 Luna variant by default; use the supported `none` reasoning-effort baseline for structured learning generation; disable hidden SDK retries; sample representative excerpts across the whole document; run model calls off the web event loop; expose coverage and route-building as separate progress stages; preserve and reuse completed coverage; map API error classes to specific recovery messages; close interrupted activity records at restart; give the model short source-reference aliases that are mapped back to real IDs before validation; and deterministically remove impossible prerequisite links before the final map integrity check
- Real verification: the same PDF completed source coverage in 18.9 seconds and a five-concept knowledge map in 13.9 seconds; the server-side key and generated content were not printed
- Full live verification: the isolated current product flow passed automatic learning-path generation, path confirmation, starting response, Tutor, Quiz, structured feedback, recommendation-free `LearningEvidence`, and exactly-one-action Agent selection with `gpt-5.6-luna`
- Browser verification: a saved map restored correctly with five grounded concepts, one dominant start action and source-location controls; all visible text was English, `body` background image was `none`, and desktop document width matched the viewport

## Product-positioning refinement — focus-first, AI-first

- Status: complete
- Date: 2026-07-21
- Trigger: the homepage headline described converting existing material into a session but did not state the actual outcome: starting faster, building a knowledge structure, sustaining attention and finishing learning
- Decision: position StartFrame as **AI-first, not AI-only**. AI and technical learning are the launch wedge and demonstration focus, while the current source-grounded learning loop remains usable for other text-based subjects
- Scope boundary: do not claim AI-only differentiation until the product includes code execution/debugging, formula and architecture-diagram understanding, an AI prerequisite knowledge base, technical freshness checks and AI-specific evaluations
- UI correction: replaced the material-conversion headline with “Start faster. Build real understanding. Finish what you set out to learn.”; changed the learner-facing ADHD label to “Focus-friendly”; and identified AI and technical learning as the initial focus without restricting uploads
- Artifact alignment: updated the production homepage, low-fidelity prototype, full specification, scope decision, README, judge instructions, Devpost copy and video script
- Verification: 49 automated tests passed; JavaScript and diff checks passed; browser inspection confirmed the new English copy, flat background, no horizontal overflow and removal of the previous headline

## Product-flow simplification — explanation before evaluation

- Status: complete
- Date: 2026-07-21
- Trigger: learner review found the suggested outcome, duplicate route card, first-action card, pre-learning response and full-panel source preview redundant and reported that the actual teaching content appeared too late
- Decision: keep one concise knowledge framework, remove route-adjustment decisions and the pre-test, then open the first concept explanation directly; source transparency remains available as a lightweight disclosure inside the explanation
- Implementation: added a versioned direct-start endpoint; starts the first route concept without a draft or baseline answer; concept map outputs now carry teaching key points and a concrete example; legacy saved maps receive a grounded source-based explanation fallback; upload and focus UI were simplified; Tutor, Quiz, recall, feedback, LearningEvidence, Agent and four-gate search boundaries remain unchanged
- Artifact alignment: updated the production UI, full specification, information architecture, end-to-end flow, screen specification, data/API contract, final decisions, prototype, README, judge guide, submission copy, video script and verification report
- Verification: 50 automated tests passed; Python compilation and JavaScript syntax passed; browser inspection confirmed upload → concise framework → direct first explanation, expandable inline source text, no pre-test view, no preview panel, English-only copy, flat backgrounds and exact desktop viewport width

## Quiz-flow simplification — immediate answer feedback

- Status: complete
- Date: 2026-07-22
- Trigger: learner review found repeated uploaded-material rows, practice-boundary copy, locked hint cards, the five-part feedback layout, next-micro-action card and separate Evidence handoff distracting and difficult to interpret
- Decision at that point: compress Quiz to one question and one immediate explanation. This was superseded by the interactive-framework refinement below after learner testing showed that one item was too weak to check a concept reliably.
- System boundary: source references, structured feedback, `LearningEvidence` and the exactly-one-action Agent remain fully enforced on the server; only their learner-facing presentation is compressed. A quiet source-origin line remains without file/page repetition
- Flow correction: Continue completes the evidence boundary and requests the Agent automatically; the separate Evidence review/"Ask Agent" task is replaced by a minimal loading state, and the next-step screen shows one action with optional alternatives in a disclosure
- Verification: 50 automated tests passed; JavaScript syntax, Python compilation, diff hygiene, English-only and no-gradient scans passed; the browser completed Quiz → inline hint → incorrect answer → answer-level explanation → automatic next-step preparation, with exact 1280 px viewport width and no technical boundary panels

## Product-flow refinement — interactive framework and compact three-question check

- Status: complete
- Date: 2026-07-22
- Trigger: learner review found the map visually static, the one-question Quiz too shallow, the practice selector unclear, and the Session status and Agent alternative-path panels distracting
- Decision: every concept map node is selectable and reveals its definition, role and prerequisites without changing the active learning route; each multiple-choice check contains exactly three questions covering definition, mechanism and application; free recall remains one response
- UI correction: changed the focus workspace to a two-column map-and-lesson layout; removed the entire Session status rail and the Agent alternative-path form; reduced test selection to “Multiple choice · 3 questions” and “Free recall · 1 response”; changed Quiz feedback to a score plus one concise explanation per question
- Boundary preservation: map exploration never bypasses Agent-controlled progression; answer keys remain server-side; `LearningEvidence` remains observations only; the Agent still returns exactly one next action; external search gates are unchanged
- Verification: 50 automated tests passed; JavaScript syntax, Python compilation, diff hygiene, English-only and no-gradient scans passed; a real `gpt-5.6-luna` browser flow generated three distinct questions, saved three independent answers, returned 3/3 with three item explanations, continued automatically to one next action, and opened the next concept lesson
- Browser layout audit: no horizontal overflow at 1280 px, no gradient backgrounds, no Chinese learner-facing copy, no Session status rail and no “Choose another path” interface

## StartOne Momentum Loop — one clear step and automatic continuation

- Status: complete
- Date: 2026-07-22
- Trigger: learner review found that the product still did not clearly reduce activation friction, visualize the knowledge structure, sustain attention, celebrate real progress or move smoothly from one learning task to the next; the StartFrame name was also ambiguous
- Product decision: rename the product to **StartOne** and define the StartOne Momentum Loop as start one clear step → see the whole framework → focus on one concept → retrieve once → receive truthful feedback → continue automatically
- UI correction: replaced the homepage promise, added a connected horizontal knowledge framework, added prerequisite/current/next relationship diagrams and memory anchors, made Tutor secondary to the lesson, renamed the retrieval choices to “Check this concept · 3 quick questions” and “Explain it yourself · 1 response”, and changed feedback to one truthful Small win with Keep going
- Information reduction: removed the learner source-coverage page and the ordinary Agent decision page; coverage, candidate gaps, LearningEvidence and Agent action validation remain enforced server-side, while only a real external-search request exposes the named gap in the required confirmation view
- Momentum correction: safe Agent actions apply automatically. Browser testing caught an old timer rule that ended an unfinished route after a correct 3/3 result; the rule now forbids automatic finish while a validated next concept exists and marks the mastered final concept complete before summary generation
- Boundary preservation: uploaded material remains primary; Tutor explains and guides the current concept; Quiz, recall, hints, feedback, encouragement and remediation stay inside Guided Mastery; LearningEvidence contains observations only; Agent returns one action; external search still requires all four gates and exact user confirmation
- Verification: 52 automated tests passed; Python compilation, JavaScript syntax, diff hygiene, English-only UI and no-gradient scans passed
- Browser verification: a fresh real-model session created from pasted material generated a four-concept visual framework, rendered a grounded concept explanation and relationship diagram, produced three distinct Quiz questions, returned 3/3 with one explanation per item, and opened concept 2 of 4 automatically after Keep going with no Agent or coverage page
- Browser layout audit: at 1280 px, document width equaled viewport width, the graph nodes formed one connected row, no gradient or Chinese learner text appeared, and no horizontal overflow was present
