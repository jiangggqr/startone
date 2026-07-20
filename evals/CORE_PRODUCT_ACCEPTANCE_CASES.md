# Core product acceptance cases

## C01 Grounded upload

Given a valid Markdown file, every concept and activity source reference resolves to a stored heading and line range.

## C02 Partial file failure

Given two valid files and one unreadable PDF, valid files remain usable and the user receives a clear recovery action for the failed file.

## C03 No fabricated location

When a model returns an unknown source reference, the server rejects it and the UI does not render a fake page or line.

## C04 Start action

The first action lasts 60–120 seconds, contains one instruction and one completion condition, and does not require prior planning.

## C05 Tutor boundary

Tutor answers within the active concept, records a gap signal when necessary, and does not change route or start search.

## C06 Quiz quality

Each distractor has a plausible misconception tag. The correct answer is not sent to the client before submission.

## C07 Recall paraphrase

A semantically correct paraphrase receives credit even when wording differs from the reference answer.

## C08 Feedback quality

Feedback identifies mastered content, gaps, a compact correction, a concrete next action and behavior-specific encouragement.

## C09 Evidence purity

LearningEvidence contains observations only and fails validation if it includes a recommendation or next action.

## C10 Agent single action

Every Agent decision contains exactly one allowed action and a learner-facing reason.

## C11 Prerequisite return

An inserted prerequisite preserves `return_to_concept_id` and returns to the original concept after completion.

## C12 Search gates

No network call occurs without all gates: session permission, named gap, Agent request and user confirmation.

## C13 Search failure recovery

A timeout or no-result response preserves the current session and allows learning to continue from uploaded material.

## C14 Resume

Refresh during an unfinished recall restores the active concept, draft answer, hint depth and session time state.

## C15 User override

The user can select another valid next path; the override is recorded without punishment or loss of progress.

## C16 Session end

Ending a session creates a summary and a specific next 1–2 minute restart action.

## C17 Agent evidence basis

An Agent decision may use time, route and source coverage as constraints, but it cannot claim mastery or misconception without validated LearningEvidence.

## C18 Local versus global action

Feedback `next_micro_action` stays inside the active concept and fails validation if it encodes route change, search or session end.

## C19 Workspace isolation

A source, session, draft or export owned by another anonymous workspace returns a non-disclosing permission error and never leaks metadata.

## C20 Location schemes

PDF chunks require page and page-chunk positions; Markdown/TXT chunks require heading and line ranges; pasted text requires a paragraph number. Invalid mixed or missing locations fail validation.

## C21 Tutor evidence aggregation

Tutor messages persist individually, but evidence is created only at a checking boundary, an explicit unresolved-confusion signal or Tutor close.

## C22 Copy and deletion

Copying a session may share an immutable checksum-addressed blob. Deleting one session preserves blobs with remaining references; deleting the last reference removes the blob.
