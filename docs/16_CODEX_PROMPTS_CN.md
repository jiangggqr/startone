# 16 可直接复制给 Codex 的分阶段 Prompt

每次只执行一个 Prompt。先计划，后实现，最后测试和浏览器验证。

---

## Prompt 0：建立可运行骨架

```text
Goal:
Create Milestone 0, the clean runnable foundation for StartFrame Agent.

Read first:
AGENTS.md, PLANS.md, STARTFRAME_FULL_SPEC_CN.md,
docs/02_INFORMATION_ARCHITECTURE_CN.md,
docs/11_PRODUCTION_UX_STANDARDS_CN.md,
docs/12_ACCESSIBILITY_RESPONSIVE_CN.md,
docs/13_DATA_AI_API_CONTRACTS.md,
and inspect prototype screen 01.

Constraints:
- Python 3.11+, FastAPI, Uvicorn, SQLite, static HTML/CSS/JS.
- No Node.js build system.
- Keep all specification and prototype files.
- Do not implement uploads, AI, Tutor, Quiz, Agent or search yet.

Implement:
1. FastAPI app on port 8000.
2. GET /api/health.
3. Accessible app shell with global navigation; runtime and evaluator controls stay outside the learner UI.
4. Static homepage matching prototype screen 01 at low-fidelity level.
5. SQLite schema version table.
6. Config and .env.example with demo/real mode, but no OpenAI call.
7. requirements.txt, .gitignore, run and test commands.
8. One smoke test and one basic browser/manual check.

Process:
- First list exact files and tests.
- Implement.
- Run tests, start the server and inspect desktop and mobile widths.
- Report command output, browser checks, limitations and changed files.
- Update PLANS.md and CODEX_BUILD_LOG.md only after verification.
```

---

## Prompt 1：来源上传、解析和真实定位

```text
Goal:
Implement Milestone 1: source ingestion, stable grounding and production states.

Read first:
docs/05_SCREEN_AND_INTERACTION_SPEC_CN.md screens 03, 04 and 16,
docs/06_COMPONENTS_AND_STATES_CN.md,
docs/10_SOURCE_GROUNDING_AND_SEARCH_CN.md,
docs/13_DATA_AI_API_CONTRACTS.md,
evals/CORE_PRODUCT_ACCEPTANCE_CASES.md,
and inspect prototype screens 03, 04, 16 and 20.

Implement:
- PDF, Markdown, TXT and pasted text.
- Real PDF pages and Markdown/TXT heading plus line ranges.
- Stable source/chunk IDs, checksums and SQLite persistence.
- Local retrieval using FTS5 when available.
- File list, parse progress, partial-success, failure and retry/remove UI.
- Source structure, snippet preview and source viewer.
- Configurable file limits and clear validation.
- Sample data fixtures.

Do not implement:
- Knowledge map generation
- Tutor, activities, Agent or web search

Acceptance:
- Every source reference resolves to a real stored location.
- Refresh preserves source metadata.
- Scanned/unreadable PDFs fail clearly without invented content.
- Successful files remain usable when another file fails.
- Relevant unit, integration and browser checks pass.
```

---

## Prompt 2：设置、来源覆盖、知识地图和启动动作

```text
Goal:
Implement Milestone 2: automatic material analysis, source coverage, knowledge map, route and first action without a learner setup form.

Read first:
prototype screens 02, 04, 05 and 06,
docs/03_END_TO_END_USER_FLOW_CN.md,
docs/07_ADHD_INFORMED_UX_CN.md,
docs/10_SOURCE_GROUNDING_AND_SEARCH_CN.md,
docs/13_DATA_AI_API_CONTRACTS.md.

Implement:
1. Goal, prior knowledge, time, energy, language and support preferences.
2. Search suggestion permission with runtime-confirmation explanation.
3. SourceCoverage Structured Output.
4. 2–5 concept map with dependencies and validated source refs.
5. Named source gaps that do not automatically trigger search.
6. Editable route and estimated time.
7. One StartAction lasting 60–120 seconds with completion condition.
8. Deterministic Demo fixtures and real GPT-5.6 code path.
9. Loading, invalid-output and retry states.

Boundaries:
- Do not implement post-activity Agent decisions.
- Do not call web search.
- Do not send whole documents when relevant chunks suffice.

Verify upload-to-start-action in browser and add contract/grounding tests.
```

---

## Prompt 3：生产级专注学习工作区

```text
Goal:
Implement Milestone 3: the complete focus-session shell before activity intelligence.

Read first:
prototype screens 07, 17, 18, 19, 20 and 21,
docs/02_INFORMATION_ARCHITECTURE_CN.md,
docs/05_SCREEN_AND_INTERACTION_SPEC_CN.md,
docs/06_COMPONENTS_AND_STATES_CN.md,
docs/07_ADHD_INFORMED_UX_CN.md,
docs/11_PRODUCTION_UX_STANDARDS_CN.md,
docs/12_ACCESSIBILITY_RESPONSIVE_CN.md.

Implement:
- Desktop three-column focus view.
- Tablet collapsible layout and mobile single-column layout.
- One active concept and one dominant recommended action.
- Compact concept map, source viewer, session status and optional time display.
- Autosave, offline/local draft, refresh resume and save-conflict handling.
- Pause, summary shell, history, settings, privacy and deletion confirmation.
- Loading, empty, partial-success, API-error and recovery components.
- Tutor, Quiz and Recall entrances may be disabled with accurate status until Milestone 4.

Acceptance:
- Refresh restores exact position and draft.
- Core shell works with keyboard.
- Focus indicators and dialog focus return are visible.
- Desktop and mobile browser flows match prototype behavior.
- No long unprioritized task list.
```

---

## Prompt 4A：Contextual Tutor

```text
Goal:
Implement Milestone 4A: source-aware contextual Tutor and graduated guidance.

Read first:
prototype screen 08,
docs/08_GUIDED_MASTERY_LOOP_CN.md,
docs/10_SOURCE_GROUNDING_AND_SEARCH_CN.md,
docs/13_DATA_AI_API_CONTRACTS.md.

Implement:
- Quick actions and free questions.
- Context: active concept, source chunks, map relation, first learner response, recent attempts and confusion signals.
- TutorResponse Structured Output.
- Guidance ladder: clarify, direction, structure, keywords, partial example, concise explanation, checking question.
- Source origin labels and validated refs.
- Message persistence, resume, streaming/cancel state and retry.
- Prerequisite/source-gap signals saved for later evidence.
- Deterministic Demo conversation.

Boundaries:
- Tutor cannot change route, grade Quiz/Recall, make Agent decisions or start search.
- Default explanation is concise and non-metaphorical.
- Missing coverage is declared, not invented.

Verify at least three turns, repeated confusion, refresh resume and keyboard operation.
```

---

## Prompt 4B：Quiz 与自由复述

```text
Goal:
Implement Milestone 4B: grounded practice and attempt capture.

Read first:
prototype screens 09 and 10,
docs/08_GUIDED_MASTERY_LOOP_CN.md,
docs/13_DATA_AI_API_CONTRACTS.md.

Implement:
1. One-question single-select Quiz.
2. Misconception-based distractors and option-specific hidden explanations.
3. Free-recall prompt with expected key points and acceptable paraphrases.
4. Progressive 0–3 level hints.
5. Attempt persistence: answer, selected option, hint depth, elapsed time and edits.
6. Source refs and origin labels.
7. Loading, submission, retry and refresh-resume states.
8. Deterministic Demo activities.

Do not implement final feedback wording, evidence aggregation or Agent decisions in this milestone.

Verify one Quiz and one recall flow up to successful attempt submission on desktop and mobile.
```

---

## Prompt 4C：反馈、鼓励、补救练习与 LearningEvidence

```text
Goal:
Implement Milestone 4C: assessment output, behavior-specific encouragement, remedial practice and normalized evidence.

Read first:
prototype screens 11 and 12,
docs/07_ADHD_INFORMED_UX_CN.md,
docs/08_GUIDED_MASTERY_LOOP_CN.md,
docs/13_DATA_AI_API_CONTRACTS.md.

Implement:
- Unified FeedbackOutput with mastered, missing, misconception, correction, next micro-action, encouragement and source refs.
- Option-specific Quiz feedback.
- Recall key-point coverage that accepts paraphrases.
- Behavior-specific encouragement and prohibited-phrase tests.
- Remedial options: simpler explanation, smaller question, concrete example, contrast and rephrase.
- Loop protection after repeated ineffective strategy.
- Normalized LearningEvidence with no recommendation fields.
- Immediate UI feedback and persistence.

Acceptance:
- No generic praise-only feedback.
- No personality or medical claims.
- Evidence contains observations only.
- Source refs validate.
- Browser flow proceeds from attempt to feedback to remedial to evidence.
```

---

## Prompt 5：Adaptive Planning Agent

```text
Goal:
Implement Milestone 5: bounded adaptive next-step decisions.

Read first:
prototype screen 13,
docs/09_ADAPTIVE_AGENT_CN.md,
docs/13_DATA_AI_API_CONTRACTS.md,
evals/CORE_PRODUCT_ACCEPTANCE_CASES.md.

Implement:
- AgentDecision Structured Output with exactly one enum action.
- Evidence, remaining time, prerequisites, source coverage and retry history as input.
- Server-validated tools/transitions for all eight actions.
- Learner-facing reason, estimate and target.
- User override path and audit record.
- Prerequisite insertion with return path.
- Loop protection and safe session end.
- Deterministic decision fixtures and real model path.

Boundaries:
- Agent cannot teach, grade, write feedback or search directly.
- request_search only creates a pending request.
- Invalid or impossible decisions are rejected server-side.

Verify normal progression, retry, activity switch, prerequisite insertion/return, user override and safe finish.
```

---

## Prompt 6：受控外部搜索

```text
Goal:
Implement Milestone 6: controlled external supplementation.

Read first:
prototype screens 14 and 15,
docs/10_SOURCE_GROUNDING_AND_SEARCH_CN.md,
docs/11_PRODUCTION_UX_STANDARDS_CN.md,
docs/13_DATA_AI_API_CONTRACTS.md.

Implement:
1. Four gates: session permission, validated named SourceGap, Agent request_search and runtime user confirmation.
2. Runtime confirmation page showing gap, goal and alternatives; the execute endpoint revalidates all four gates.
3. OpenAI Responses API web_search in real mode.
4. Deterministic mock results in internal acceptance mode only.
5. Small candidate set with title, URL, publisher, selection reason and filled gap.
6. Preview, select, ignore and retry.
7. Persistent external source refs and labels.
8. Timeout, no-results, inaccessible-source and user-decline recovery.

Acceptance:
- Permission off means no network call.
- No named gap means no search.
- No runtime confirmation means no search.
- Search failure preserves session.
- External content is never labeled uploaded.
- User can continue without search.
```

---

## Prompt 7：端到端生产加固

```text
Goal:
Complete Milestone 7 and make every specified flow robust and testable.

Read all docs, prototype screens 00–21, and evals/.

Tasks:
- Run and complete all unit, integration, contract and browser tests.
- Implement any missing loading, empty, partial-success, error, offline, save-conflict and recovery states.
- Verify desktop, tablet and mobile layouts.
- Perform keyboard-only and focus-management checks.
- Verify source origin and citation validation everywhere.
- Verify Agent/Tutor boundaries and search gates.
- Test the no-key deterministic fixture path end to end without exposing it in learner UI.
- Run one real GPT-5.6 smoke flow without committing secrets.
- Review privacy, file handling and HTML escaping.
- Remove dead code, caches and stale fixtures.

Do not call the work complete until every acceptance case has an explicit result.
```

---

## Prompt 8：提交准备

```text
Goal:
Prepare StartFrame Agent for judging and submission.

Implement or update:
- Final README with clean installation, internal deterministic tests, real product mode and judge path.
- License.
- Sample data and expected demo behavior.
- Deployment instructions or reliable local test path.
- Architecture and product screenshots generated from the real app.
- Under-three-minute video script and shot list.
- Devpost project description and category rationale.
- CODEX_BUILD_LOG.md with Codex acceleration and human decisions.
- Security check for API keys, private data, databases and caches.
- Final test report with exact commands.

Also remind the user to run /feedback in the main Codex development thread and record the Session ID.
```
