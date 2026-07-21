# StartFrame Agent verification report

Date: 2026-07-21  
Application mode: deterministic Demo  
Automated result: `43 passed`  
Browser widths exercised: 390 px, 640 px zoom-equivalent, and desktop  
Live GPT-5.6 status: contract-tested; one live smoke test remains pending a server-side key

## Core product cases

| Case | Result | Verification evidence |
|---|---|---|
| C01 Grounded upload | Pass | Markdown/PDF/pasted parsing tests plus browser source previews resolve exact saved locations. |
| C02 Partial file failure | Pass | Mixed-upload and blank-page PDF tests preserve usable sources and return recovery details. |
| C03 No fabricated location | Pass | Invalid model references fail before persistence; the UI renders only validated references. |
| C04 Start action | Pass | Generated actions are schema-bounded to 60–120 seconds and require one saved checkable response. |
| C05 Tutor boundary | Pass | Tutor persistence, gap-signal, source validation, and no-tool real contract tests pass. |
| C06 Quiz quality | Pass | Four-option misconception contract passes; answer keys and explanations remain server-only before submission. |
| C07 Recall paraphrase | Pass | Deterministic evaluator accepts meaning-level paraphrases and records key-point coverage. |
| C08 Feedback quality | Pass | Automated and browser flows verify all five feedback sections and behavior-specific encouragement. |
| C09 Evidence purity | Pass | Database/API evidence fields contain observations only; recommendation field scans pass. |
| C10 Agent single action | Pass | Deterministic and strict function-call tests return exactly one bounded action. |
| C11 Prerequisite return | Pass | Inserted prerequisite stores and executes `return_to_concept_id`. |
| C12 Search gates | Pass | Execution revalidates permission, named gap, Agent request, and exact-scope confirmation. |
| C13 Search failure recovery | Pass | Failure/cancel/ignore flows preserve the session and return to the current concept. |
| C14 Resume | Pass | Draft, hint depth, activity, concept, pause overlay, and timer recovery pass. |
| C15 User override | Pass | Only valid alternatives are accepted; override remains penalty-free and durable. |
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
| U08 Mobile core flow | Pass | Tutor, Quiz, recall, feedback, Agent, search, summary, topic fallback, settings, and data controls were exercised at 390 px without document overflow. |
| U09 Loading clarity | Pass | Upload, generation, feedback, Tutor, Agent, export, report, and search actions use specific busy text and saved-state messages. |
| U10 Partial success | Pass | Partial upload/PDF states are visibly distinct from total error and expose retry/continue actions. |
| U11 Offline save | Pass | Offline events preserve local drafts, announce pending sync, and resync on reconnect. |
| U12 Destructive confirmation | Pass | Source, session, and workspace deletion dialogs name scope, irreversibility, and cancellation. |
| U13 Search consent | Pass | Separate confirmation displays gap, scope, reason, four gates, and “No search has run.” |
| U14 AI origin labels | Pass | Uploaded, external, and AI supplemental paths remain labeled through source, map, focus, Tutor, activity, and feedback views. |
| U15 Reduced motion | Pass | OS preference and saved app preference disable scrolling/transition motion; no information depends on animation. |
| U16 Screen reader progress | Pass | Progress uses meaningful text such as current/total/completed counts in addition to visual bars. |
| U17 Route-change focus | Pass | View changes focus the new heading; errors focus their alert; source return restores the invoking citation. |
| U18 Save conflict | Pass | Browser and integration flows keep both copies visible until an explicit choice. |
| U19 Allowed alternatives | Pass | Agent UI renders only server-provided alternatives after server validation. |
| U20 Source metadata | Pass | All learning origins are visible; external candidates include URL, publisher, access time, excerpt, and selection reason. |

## Additional hardening

- Topic-only fallback is secondary to upload, uses a fixed Self-attention fixture in Demo, uses structured GPT-5.6 output in real mode, never browses, and persists as `ai_supplement`.
- Source-location reports are workspace-owned, tied to an exact chunk, exportable, and do not alter learning progress.
- History search/filter, session copy/delete, JSON/Markdown export, AI activity, full workspace deletion, larger text, reduced motion, and new-session defaults are user-accessible.
- API responses are `no-store`; CSP, frame denial, MIME sniff prevention, referrer policy, permissions policy, opener isolation, secure-cookie support, and conditional HSTS are enabled.
- Export excludes API keys, server paths, hidden answer keys, internal prompts, and model response IDs.
- Secret scan, Python compilation, dependency integrity, diff hygiene, English UI scan, and no-gradient scan pass.

## Remaining external verification

Configure `OPENAI_API_KEY` only as a server/deployment secret, set `STARTFRAME_MODE=real`, and run one live GPT-5.6 smoke flow before final submission. Demo judging does not require a key and never silently impersonates live mode.
