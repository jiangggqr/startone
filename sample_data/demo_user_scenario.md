# Fixed internal acceptance scenario

This scenario validates the deterministic fixture path. It does not ask the learner to declare a goal, prior knowledge, available time, energy, or language, and it does not place a pre-test before the first explanation.

## Starting state

- The learner starts only from uploaded or pasted material.
- Uploaded or pasted material is the only learning source; no network tool is available.
- The first concept opens with a beginner-friendly explanation; later validated learning evidence calibrates support.

## Expected path

1. Load the two built-in sample materials, or upload `transformer_notes.md` and `matrix_prerequisite.md`. Both sources appear with readable status inside the upload panel.
2. Select **Build my map and start**. The knowledge framework includes Transformer goal, self-attention, Q/K/V, scaled dot-product attention, and positional information.
3. Select **Start one focused step**. The first concept opens with its big idea, prerequisite/current/next relationship, key parts, concrete example, memory anchor, and uploaded-source disclosure.
4. The learner may inspect any map node without changing the route, then opens Tutor only if support is useful.
5. Tutor guides the active concept and can help the learner connect relevance comparison with weighted aggregation; it cannot change the route, request material or introduce outside facts.
6. The learner completes the three-question Quiz or one free-recall response. A representative partial recall covers 2/3 key points.
7. Feedback shows the score or result, checks each answer, explains the specific gap around weighted aggregation, and records factual `LearningEvidence` internally.
8. If support is needed, a smaller weighted-sum remedial activity remains inside the Guided Mastery Loop; weighted sum is not promoted to a separate route concept.
9. The learner selects **Keep going**. The Agent selects exactly one action from validated evidence, and the server applies a safe action automatically without a decision or alternative-path page.
10. The next focused task opens directly. If a validated blocking gap remains, `request_more_material` preserves the current concept and opens the upload area.

## Optional prerequisite branch

During Q/K/V, repeated validated difficulty with dot products can lead the Agent to insert one short prerequisite concept grounded in `matrix_prerequisite.md`. The safe action applies automatically and returns to Q/K/V after mastery.

## Optional additional-material branch

Use the one-source fixture that imports only `transformer_notes.md`. After validated evidence reveals a named dot-product prerequisite gap, the Agent may select `request_more_material` with `required_tool=open_material_upload`. The learner can add `matrix_prerequisite.md` and return to the preserved concept, or continue within the current scope. No network request occurs.
