# UI/UX acceptance cases

## U01 Primary action hierarchy

Each task screen contains at most one visually dominant primary action.

## U02 Current context

The active concept, session name, save state and source origin are available without navigating away.

## U03 Keyboard-only flow

A user can create a session, upload a fixture, confirm a path, complete Quiz/Recall, review feedback and end the session using the keyboard.

## U04 Focus management

Opening Tutor or a confirmation dialog moves focus inside; closing returns focus to the trigger.

## U05 Non-color meaning

Correct, incorrect, current, completed and locked states include text or symbols, not color alone.

## U06 Target size

Frequently used controls and all mobile primary controls are at least 44×44 CSS px; no essential target violates WCAG 2.2 minimum rules.

## U07 200% zoom

At 200% zoom, content remains readable and no core operation is lost.

## U08 Mobile core flow

At 390px width, the app has no horizontal scrolling for core content and supports Tutor, Quiz, Recall, feedback, automatic safe continuation, material-gap upload recovery and summary.

## U09 Loading clarity

Long source parsing displays a specific progress stage and provides cancellation or background continuation.

## U10 Partial success

The UI differentiates partial success from total failure and offers a clear next step.

## U11 Offline save

Offline draft status is visible and the user is told what will sync later.

## U12 Destructive confirmation

Deleting a source, session or all data clearly states scope and offers cancel.

## U13 Material-gap recovery

The user sees the named gap and why it matters, while the current concept remains active. The primary action opens upload; the secondary action continues the current scope.

## U14 AI origin labels

Uploaded or pasted material is consistently labeled as the source. AI-generated wording is disclosed as generated from that material and never shown as a second source.

## U15 Reduced motion

With reduced-motion preference, no essential information depends on animation and countdowns do not pulse.

## U16 Screen reader progress

Progress is announced as meaningful text such as “2 of 5 concepts completed,” not only a percentage.

## U17 Route-change focus

After an in-app route or screen change, focus moves to the new main heading or error summary without trapping the keyboard.

## U18 Save conflict

A conflict keeps both local and server drafts visible until the user explicitly selects or merges a version; no input is silently overwritten.

## U19 Automatic safe continuation

After Keep going, the learner sees no Agent decision or alternative-path page. The server applies one validated safe action automatically; `request_more_material` preserves the concept and opens upload, and prerequisite insertion remains unavailable without supporting evidence.

## U20 Source metadata

Every concept, activity, feedback and example resolves to uploaded material. Generated explanations disclose that they were generated from the learner's material and retain verified source references.
