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
→ path_confirmed
→ start_action
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
concepts[]
edges[]
recommended_route[]
start_action
source_gaps[]
```

### StartAction

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

### TopicSourceOutput

```text
title
overview
sections[] {heading, explanation}
verification_note
```

This output is available only for the secondary topic-only fallback. It uses no search tool, is persisted with `source_origin=ai_supplement`, and never claims uploaded or externally cited provenance.

### QuizActivityOutput

```text
question
options[] {id, text, misconception_tag}
correct_option_id
explanation_by_option
hint_levels[]
source_origin
source_refs[]
```

The correct option is stored server-side and not sent to the client before submission.

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

### Session and setup

- `POST /api/sessions`
- `GET /api/sessions/{id}`
- `PATCH /api/sessions/{id}`
- `POST /api/sessions/{id}/pause`
- `POST /api/sessions/{id}/resume`
- `DELETE /api/sessions/{id}`
- `POST /api/sessions/{id}/copy`

### Sources

- `POST /api/sessions/{id}/sources`
- `POST /api/sessions/{id}/pasted-sources`
- `POST /api/sessions/{id}/topic-source`
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
- `POST /api/sessions/{id}/start-action/complete`
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

## 6. Demo and real modes

### Demo mode

- deterministic fixtures
- no API key
- visible Demo label
- mock search results
- stable judge path
- a normal fixture containing `transformer_notes.md` and `matrix_prerequisite.md`
- a controlled-search fixture containing only `transformer_notes.md`
- one fixed topic-only `Self-attention` AI-supplement fixture

### Real mode

- server-side OpenAI key
- Responses API
- schema validation
- real web search only after gates
- default model alias `gpt-5.6`, configurable on the server

Demo data must never be presented as a real model response.

The real OpenAI path begins in Milestone 2. Missing credentials, refused output, invalid schemas and invalid source references return explicit recoverable errors; they never silently switch to Demo mode.
