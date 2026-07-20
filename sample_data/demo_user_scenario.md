# Fixed demo user scenario

## User

- Prior knowledge: basic machine learning, no detailed Transformer knowledge
- Goal: understand self-attention in 25 minutes
- Energy: medium
- Language: Simplified Chinese
- Preference: concise direct explanation, no metaphor by default
- Search permission: allowed to suggest, confirm every search

## Expected path

1. Upload `transformer_notes.md` and `matrix_prerequisite.md`. The prerequisite file is available but is not placed on the initial route.
2. Knowledge map includes Transformer goal, self-attention, Q/K/V, scaled dot-product attention and positional information.
3. First action asks the user to write one sentence about self-attention.
4. User writes: “Self-attention lets a word look at other words.”
5. Tutor guides the user to add the second action: weighted aggregation.
6. User answers Quiz correctly but recall covers only 2/3 key points.
7. Feedback recognizes the correct structure and identifies the missing precision around weighted sum.
8. Remedial exercise asks a smaller weighted-sum question; weighted sum remains a mastery point inside Self-attention rather than a separate route concept.
9. LearningEvidence records improvement.
10. Agent recommends continuing to Q/K/V.

## Optional prerequisite branch

During Q/K/V, the user says they do not understand dot products twice. The Agent inserts a short prerequisite concept grounded in `matrix_prerequisite.md`, then returns to Q/K/V.

## Optional search branch

Use the separate controlled-search fixture that imports only `transformer_notes.md`. The Agent may identify a named dot-product prerequisite gap only after validated evidence. Session permission, the named gap, Agent `request_search`, and runtime user confirmation are all required before any external search occurs.
