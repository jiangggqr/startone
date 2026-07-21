# StartOne verification report

Date: 2026-07-22
Application verification: deterministic fixtures, isolated real GPT-5.6 smoke flow, and public deployment smoke flow
Automated result: `52 passed`
Browser widths exercised: 390 px, 640 px zoom-equivalent, and desktop  
Live GPT-5.6 status: passed locally on 2026-07-21 and at https://startone-learning.onrender.com on 2026-07-22

## Core product cases

| Case | Result | Verification evidence |
|---|---|---|
| C01 Grounded upload | Pass | Markdown/PDF/pasted parsing tests plus inline citations resolve exact saved locations. |
| C02 Partial file failure | Pass | Mixed-upload and blank-page PDF tests preserve usable sources and return recovery details. |
| C03 No fabricated location | Pass | Invalid model references fail before persistence; the UI renders only validated references. |
| C04 Direct start | Pass | The knowledge framework opens the first beginner-friendly explanation without a setup form or pre-test. |
| C05 Tutor boundary | Pass | Tutor persistence, gap-signal, source validation, and no-tool real contract tests pass. |
| C06 Quiz quality | Pass | Every concept Quiz contains three four-option questions covering definition, mechanism and application; answer keys and explanations remain server-only before submission. |
| C07 Recall paraphrase | Pass | Deterministic evaluator accepts meaning-level paraphrases and records key-point coverage. |
| C08 Feedback quality | Pass | The server preserves structured feedback while the browser renders correct/not-quite, answer review, one rationale and Keep going. |
| C09 Evidence purity | Pass | Database/API evidence fields contain observations only; recommendation field scans pass. |
| C10 Agent single action | Pass | Deterministic and strict function-call tests return exactly one bounded action. |
| C11 Prerequisite return | Pass | Inserted prerequisite stores and executes `return_to_concept_id`. |
| C12 Search gates | Pass | Execution revalidates permission, named gap, Agent request, and exact-scope confirmation. |
| C13 Search failure recovery | Pass | Failure/cancel/ignore flows preserve the session and return to the current concept. |
| C14 Resume | Pass | Draft, hint depth, activity, concept, pause overlay, and exact-state recovery pass. |
| C15 Automatic continuation | Pass | Safe Agent actions execute without a learner decision page; a search request still stops at the confirmation boundary. The compatibility override endpoint remains server-validated but is not exposed in the product UI. |
| C16 Session end | Pass | `finish_session` reaches a durable summary with a concrete 1–2 minute restart action. |
| C17 Agent evidence basis | Pass | Agent tests prove learning-performance claims originate only from validated evidence. |
| C18 Local versus global action | Pass | Feedback micro-actions are rejected if they encode route, search, or finish behavior. |
| C19 Workspace isolation | Pass | Independent cookies cannot read or report another workspace's session, source, or metadata. |
| C20 Location schemes | Pass | PDF page/chunk, text heading/line, and pasted paragraph schemes are tested separately. |
| C21 Tutor evidence aggregation | Pass | Tutor close creates one factual boundary record rather than evidence per message. |
| C22 Copy and deletion | Pass | Copied sessions share immutable blobs; only deletion of the final reference removes the file. |

## UI/UX cases

| Case | Result | Verification evidence |
|---|---|---|
| U01 Primary action hierarchy | Pass | Every tested task view had at most one visible `.button-primary`. |
| U02 Current context | Pass | Focus/Tutor/activity views expose session, concept, saved state, and origin without leaving the task. |
| U03 Keyboard-only flow | Pass | Core controls are native links, buttons, inputs, radios, selects, details, and dialogs; route headings and dialog focus behavior were exercised across the full milestone browser runs. |
| U04 Focus management | Pass | Tutor and all confirmation/report dialogs move focus inside and restore it to the invoking control. |
| U05 Non-color meaning | Pass | Text, symbols, status labels, and `aria-current` accompany every state. |
| U06 Target size | Pass | The 390 px computed audit found no visible control below 24×24 CSS px; primary/frequent controls meet the 44 px product target. |
| U07 200% zoom | Pass | The 640 px zoom-equivalent audit retained all core controls with document width equal to viewport width. |
| U08 Mobile core flow | Pass | Knowledge map, Tutor, Quiz, recall, feedback, automatic safe continuation, search confirmation, summary, settings, and data controls were exercised at 390 px without document overflow. |
| U09 Loading clarity | Pass | Upload, generation, feedback, Tutor, next-step preparation, export, report, and search actions use specific busy text and saved-state messages. |
| U10 Partial success | Pass | Partial upload/PDF states are visibly distinct from total error and expose retry/continue actions. |
| U11 Offline save | Pass | Offline events preserve local drafts, announce pending sync, and resync on reconnect. |
| U12 Destructive confirmation | Pass | Source, session, and workspace deletion dialogs name scope, irreversibility, and cancellation. |
| U13 Search consent | Pass | Separate confirmation displays gap, scope, reason, four gates, and “No search has run.” |
| U14 AI origin labels | Pass | Uploaded, external, and AI supplemental paths remain labeled through source, map, focus, Tutor, activity, and feedback views. |
| U15 Reduced motion | Pass | OS preference and saved app preference disable scrolling/transition motion; no information depends on animation. |
| U16 Screen reader progress | Pass | Progress uses meaningful text such as current/total/completed counts in addition to visual bars. |
| U17 Route-change focus | Pass | View changes focus the new heading; errors focus their alert; source return restores the invoking citation. |
| U18 Save conflict | Pass | Browser and integration flows keep both copies visible until an explicit choice. |
| U19 Automatic safe continuation | Pass | Keep going requests exactly one validated Agent action and applies safe actions without an Agent or alternative-path page; `request_search` still stops for exact-scope confirmation. |
| U20 Source metadata | Pass | All learning origins are visible; external candidates include URL, publisher, access time, excerpt, and selection reason. |

## Additional hardening

- Upload or pasted material is the only learning entry; the app has no topic-only substitute or setup form.
- Automated coverage verifies upload → AI-selected knowledge framework → direct first explanation → Tutor/Quiz/recall visibility.
- Quiz browser coverage verifies three centered question groups, one quiet source-origin line, optional inline hints, no repeated file/page rows or system-boundary copy, and immediate per-question explanations.
- Continue from feedback completes recommendation-free evidence, requests one Agent action automatically, and skips the former learner-facing Evidence review task.
- Source-location reports are workspace-owned, tied to an exact chunk, exportable, and do not alter learning progress.
- History search/filter, session copy/delete, JSON/Markdown export, AI activity, full workspace deletion, larger text, reduced motion, and new-session defaults are user-accessible.
- API responses are `no-store`; CSP, frame denial, MIME sniff prevention, referrer policy, permissions policy, opener isolation, secure-cookie support, and conditional HSTS are enabled.
- Public-release defaults enforce 20 sessions and 50 sources per anonymous workspace; quota failures preserve existing data and return a recoverable English error envelope.
- Export excludes API keys, server paths, hidden answer keys, internal prompts, and model response IDs.
- The browser check loaded the standard two-source fixture; at 390 px the document width equaled the viewport, no visible control was below 24×24 CSS px, no Chinese UI was present, and the computed body background image was `none`.
- The 2026-07-22 desktop browser pass completed a real three-question Quiz, reviewed the score and per-question explanations, selected Keep going, and automatically opened concept 2 of 4 without an Agent decision page. Width matched the 1280 px viewport; no Chinese text or gradient was present.
- The public Render deployment repeated paste → four-node real GPT-5.6 map → explanation → three-question Quiz → 3/3 feedback → automatic concept 2 of 4 without a sign-in or learner-supplied API key.
- Secret scan, Python compilation, dependency integrity, diff hygiene, English UI scan, no-gradient scan, and deployment YAML parsing pass.

## Live GPT-5.6 verification

With `OPENAI_API_KEY` configured only in the ignored local `.env`, `scripts/live_smoke.py` passed an isolated temporary-database flow using the configured GPT-5.6 model for source coverage, knowledge-map generation, Tutor guidance, Quiz generation, structured feedback and one bounded Agent decision. The flow also rechecked recommendation-free `LearningEvidence` and the Agent's exactly-one-action boundary. No credential or generated learning content was printed or persisted to the normal application database. Real web-search request shape and citation filtering remain contract-tested with a fake Responses client; the public deployment uses the server-side real-model path.

On 2026-07-21, a 49-page, 72-chunk uploaded PDF reproduced the visible learning-path failure. The corrected production path used `gpt-5.6-luna`, sampled representative excerpts across the full document, and completed real source coverage in 18.9 seconds plus the five-concept knowledge map in 13.9 seconds. The API key and generated learning content were not printed. The browser then restored a saved map, showed verified source locations, contained no Chinese UI text, used no background image or gradient, and matched the viewport width at desktop size.

After source-reference aliasing and deterministic route-link normalization were added, the isolated current-flow smoke script passed automatic `gpt-5.6-luna` learning-path generation, concept explanation, Tutor, Quiz, structured feedback, recommendation-free `LearningEvidence`, and the Agent's exactly-one-action decision. The regression count is updated in `PROJECT_STATUS.md` after each product-flow change.
