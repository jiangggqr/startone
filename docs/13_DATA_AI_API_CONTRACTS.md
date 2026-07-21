# 13 Data, AI and API contracts

This file defines semantic contracts. It is not application code.

## 1. Session state machine

Primary learning states:

```text
idle
→ session_created
→ sources_processing
→ sources_reviewable
→ path_drafting
→ learning_concept
→ practicing
→ feedback_shown
→ remedial_practice (optional)
→ evidence_ready
→ agent_decision
→ learning_concept | search_confirmation | session_summary

search_confirmation
→ search_running | learning_concept (declined)
search_running
→ search_results | learning_concept (failed)
search_results
→ learning_concept (selected or ignored)

session_summary (terminal saved summary; a copied session starts with fresh learning progress)
```

Pause is an overlay, not a terminal point in the linear state machine. A pause stores the current primary state in `resume_state`, sets `is_paused = true`, and blocks learning mutations until resume restores it. Drafts and timer state are persisted separately.

Every server mutation must validate the workspace, current state, resource ownership and optimistic version. The client cannot directly force an invalid transition.

## 2. Core entities

### LearningSession

```text
id
workspace_id
name
goal
prior_knowledge
available_minutes
energy_level
language
support_preferences
search_permission
mode: demo | real
state
resume_state
is_paused
active_concept_id
active_activity_id
version
timer_started_at
elapsed_seconds
remaining_seconds
started_at
updated_at
last_saved_at
ended_at
```

The current recommendation is derived from the latest accepted `AgentDecision`; it is not duplicated as an unconstrained writable session field.

`goal` 由材料分析后的 `map_title` 派生。`prior_knowledge` 初始固定为未评估；产品不用开始前测试估算水平，首个概念按初学者深度讲解，之后只根据已验证活动证据逐步校准。`available_minutes` 是内部紧凑会话默认值；`energy_level` 为兼容既有数据库迁移保留且新会话写入 `NULL`。这些字段不构成用户设置表单，也不由产品 API 接收。

### Workspace

```text
id
created_at
last_seen_at
data_version
```

The workspace ID is random and scoped by a secure same-site cookie. It is never accepted from a client-provided request body.

### SourceBlob

```text
id
checksum
storage_path
byte_size
created_at
```

Blob paths are server-generated and never derived from the uploaded filename.

### SourceDocument

```text
id
workspace_id
session_id
blob_id
filename
media_type
media_kind: pdf | markdown | text | pasted
source_origin: uploaded | ai_supplement
parse_status
page_count
line_count
error_code
version
created_at
```

### SourceChunk

```text
id
source_id
heading_path
page_number
page_chunk_index
paragraph_number
start_line
end_line
start_char
end_char
text
search_text
checksum
```

Location validation by media kind:

- PDF requires `page_number`, `page_chunk_index`, `start_char`, `end_char`
- Markdown/TXT requires `heading_path`, `start_line`, `end_line`, `start_char`, `end_char`
- pasted text requires `paragraph_number`, `start_char`, `end_char`
- external web content requires an `ExternalSource` record and may include a verified text-fragment locator

Locations must come from parsing or verified retrieval, never model generation.

### SourceGap

```text
id
session_id
concept_key
description
why_needed
evidence
current_source_refs
suggested_query_scope
status: candidate | validated | resolved | dismissed
created_at
resolved_at
```

### ExternalSource

```text
id
workspace_id
session_id
source_gap_id
canonical_url
title
publisher
accessed_at
selection_reason
citation_excerpt
locator
status: candidate | selected | inaccessible | ignored
created_at
```

### Concept

```text
id
session_id
title
plain_definition
role_in_map
prerequisite_ids
order_index
status
estimated_minutes
source_refs
```

### Activity

```text
id
session_id
concept_id
type: quiz | recall | remedial
prompt
source_refs
source_origin: uploaded | external | ai_supplement
hint_levels
misconception_targets
created_at
```

### Attempt

```text
id
activity_id
raw_answer
selected_option_id
hint_depth
elapsed_seconds
submitted_at
```

### TutorMessage

```text
id
session_id
concept_id
role: user | tutor
message
guidance_level
source_origin
source_refs
confusion_signal
prerequisite_gap_signal
created_at
```

### Draft

```text
id
workspace_id
session_id
activity_id
draft_type
content
hint_depth
client_version
server_version
sync_status
updated_at
```

### LearningEvidence

```text
id
session_id
concept_id
activity_type
outcome
key_point_coverage
misconception_tags
hint_depth
elapsed_seconds
tutor_confusion_signals
remedial_result
source_gap_signal
created_at
```

`activity_type` is exactly `tutor_check | quiz | recall | remedial`. No recommendation fields are allowed. Tutor evidence is aggregated only at a checking boundary, an explicit unresolved-confusion signal, or Tutor close.

### AgentDecision

```text
id
session_id
concept_id
action
reason_for_user
estimated_minutes
target_concept_id
return_to_concept_id
required_tool
confidence
created_at
user_override
```

### SearchRequest

```text
id
workspace_id
session_id
concept_id
source_gap_id
agent_decision_id
query_scope
reason_for_user
permission_snapshot
confirmation_status
search_status
generation_mode
model
response_id
error_code
version
created_at
```

Execution additionally records `confirmed_at`, `executed_at` and `completed_at`. The server revalidates all four gates at execution time. `ExternalSource` stores the canonical public HTTPS URL, title, publisher, access time, citation excerpt, locator (empty when unavailable), selection reason, rank and status. A selected source is linked to one concept; it supplements rather than replaces uploaded material.

## 3. Structured model outputs

All model outputs must be validated against JSON Schema or equivalent typed models before persistence or rendering.

### SourceCoverage

```text
covered_concepts[]
source_gaps[] {description, why_needed, evidence, current_source_refs, suggested_query_scope}
ignored_sections[]
source_refs[]
```

### KnowledgeMapOutput

```text
map_title
concepts[] {plain_definition, key_points[2..4], concrete_example, role_in_map, prerequisite_keys, source_refs}
edges[]
recommended_route[]
source_gaps[]
```

`start_action` 只为旧数据库与 API 向后兼容保留，不再是生产学习流程的显示字段、必做任务或校准信号。

### Legacy StartAction (compatibility only)

```text
title
instruction
estimated_seconds: 60..120
completion_condition
why_this_first
```

### TutorResponse

```text
message
guidance_level
checking_question
source_origin
source_refs[]
confusion_signal
prerequisite_gap_signal
```

### QuizActivityOutput

```text
questions[3] {
  id,
  question,
  key_point,
  options[] {id, text, misconception_tag},
  correct_option_id,
  explanation_by_option
}
hint_levels[]
source_origin
source_refs[]
```

Each concept Quiz contains exactly three single-select questions covering definition, mechanism and application. Correct options, key points, misconception tags and explanations are stored server-side and are not sent to the client before submission. The existing `Attempt.selected_option_id` column stores a JSON object keyed by question ID for compatibility with the established database; it is not a single answer semantically for current Quiz records.

### RecallActivityOutput

```text
prompt
expected_key_points[]
acceptable_paraphrases[]
misconception_patterns[]
hint_levels[]
source_origin
source_refs[]
```

### FeedbackOutput

```text
mastered_points[]
missing_or_unclear_points[]
misconceptions[]
compact_correction
next_micro_action
encouragement
source_origin
source_refs[]
```

`next_micro_action` is restricted to the active concept and must not encode an Agent action, route change, search request or session end.

For a submitted Quiz, the public feedback response additionally includes a post-submission `quiz_result` projection:

```text
is_correct
correct_count
total_questions
questions[] {
  question_id,
  question_number,
  question,
  is_correct,
  selected_option_id,
  selected_option_text,
  correct_option_id,
  correct_option_text,
  explanation
}
```

This projection is never present on the pre-submission activity response. It exists only to render a familiar correct / not-quite answer review; answer keys remain server-side before submission.

### AgentDecisionOutput

```text
action: enum
reason_for_user
estimated_minutes
target_concept_id
return_to_concept_id
required_tool
confidence
```

## 4. API semantics

Implemented endpoint groups. FastAPI's generated schema at `/api/docs` is authoritative for request and response fields.

### Session and automatic preparation

- `POST /api/sessions`
- `GET /api/sessions/{id}`
- `POST /api/sessions/{id}/learning-path`（从材料自动完成覆盖、学习重点和地图生成，不接收目标、基础、时间或精力字段）
- `POST /api/sessions/{id}/pause`
- `POST /api/sessions/{id}/resume`
- `DELETE /api/sessions/{id}`
- `POST /api/sessions/{id}/copy`

### Sources

- `POST /api/sessions/{id}/sources`
- `POST /api/sessions/{id}/pasted-sources`
- `GET /api/sessions/{id}/sources`
- `GET /api/sources/{source_id}`
- `GET /api/sources/{source_id}/chunks/{chunk_id}`
- `GET /api/sources/{source_id}/progress`
- `POST /api/sources/{source_id}/cancel`
- `POST /api/sources/{source_id}/retry`
- `POST /api/sources/{source_id}/chunks/{chunk_id}/reports`
- `DELETE /api/sources/{source_id}`
- `POST /api/sessions/{id}/coverage`
- `GET /api/sessions/{id}/coverage`
- `GET /api/sessions/{id}/source-gaps`

### Path and focus

- `POST /api/sessions/{id}/path`
- `PATCH /api/sessions/{id}/path`
- `GET /api/sessions/{id}/path`
- `POST /api/sessions/{id}/path/confirm`
- `POST /api/sessions/{id}/learn/start` — 生产流程直接打开第一个概念，无开始前测试
- `POST /api/sessions/{id}/start-action/complete` — 仅供旧会话向后兼容
- `GET /api/sessions/{id}/focus`
- `PUT /api/sessions/{id}/drafts/{draft_type}` with optimistic `version`
- `GET /api/sessions/{id}/drafts`
- `POST /api/sessions/{id}/draft-conflicts/{draft_type}/resolve`

### Tutor and activities

- `POST /api/sessions/{id}/tutor/messages`
- `GET /api/sessions/{id}/tutor/messages`
- `POST /api/sessions/{id}/tutor/open`
- `POST /api/sessions/{id}/tutor/close`
- `POST /api/sessions/{id}/activities`
- `GET /api/activities/{activity_id}`
- `POST /api/activities/{activity_id}/hints/next`
- `POST /api/activities/{activity_id}/attempts`
- `POST /api/attempts/{attempt_id}/feedback`
- `GET /api/attempts/{attempt_id}/feedback`
- `GET /api/feedback/{feedback_id}`
- `POST /api/feedback/{feedback_id}/complete`
- `POST /api/feedback/{feedback_id}/remedial-activity`
- `POST /api/activities/{activity_id}/close`

### Evidence and Agent

- `GET /api/sessions/{id}/evidence`
- `POST /api/sessions/{id}/agent-decisions`
- `GET /api/sessions/{id}/agent-decisions/latest`
- `GET /api/agent-decisions/{decision_id}`
- `POST /api/agent-decisions/{decision_id}/accept`
- `POST /api/agent-decisions/{decision_id}/override`

The production client does not expose a separate Evidence review or ordinary Agent confirmation step. After the learner selects Keep going on feedback, it completes the feedback boundary, requests exactly one Agent decision and automatically accepts the safe action. `request_search` still stops at the separate search confirmation. The API separation remains mandatory so `LearningEvidence` cannot contain or silently become a recommendation.

### Search

- `POST /api/sessions/{id}/search-requests`
- `GET /api/sessions/{id}/search-requests/latest`
- `GET /api/search-requests/{id}`
- `POST /api/search-requests/{id}/confirm`
- `POST /api/search-requests/{id}/execute`
- `POST /api/search-requests/{id}/cancel`
- `POST /api/search-requests/{id}/ignore`
- `GET /api/external-sources/{id}`
- `POST /api/external-sources/{id}/select`

### Summary and records

- `GET /api/sessions/{id}/summary`
- `GET /api/sessions`
- `GET /api/export?format=json|markdown`
- `GET /api/ai-activity`
- `DELETE /api/user-data`

## 5. Error envelope

```text
error_code
user_message
recoverable
retry_after_seconds
field_errors
saved_state
request_id
```

`user_message` must be understandable without exposing stack traces. `saved_state` tells the UI what was preserved.

## 6. Internal deterministic tests and real mode

### Internal deterministic path

- deterministic fixtures
- no API key
- mock search results
- automated and local acceptance tests only; no global mode badge or evaluator control in the learner UI
- a normal fixture containing `transformer_notes.md` and `matrix_prerequisite.md`
- a controlled-search fixture containing only `transformer_notes.md`

### Real mode

- server-side OpenAI key
- Responses API
- schema validation
- real web search only after gates
- default model `gpt-5.6-luna`, configurable on the server; the low-latency GPT-5.6 variant is used for interactive learning generation

Fixture data must never be presented as a real model response or used for arbitrary public uploads.

The real OpenAI path begins in Milestone 2. Missing credentials, refused output, invalid schemas and invalid source references return explicit recoverable errors; they never silently switch to deterministic fixtures.
