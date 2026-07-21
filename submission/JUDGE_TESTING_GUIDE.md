# StartOne — judge testing guide

## Fastest product path

The public deployment needs no learner account. GPT-5.6 credentials stay on the server and never appear in the browser.

1. Open https://startone-learning.onrender.com.
2. Select **Upload material and start learning**.
3. Upload `sample_data/transformer_notes.md` from the public repository, paste your own notes, or upload any readable PDF, Markdown, or TXT file.
4. Confirm that both file status and the next action appear inside the upload panel, then select **Build my map and start**.
5. Review the AI-selected focus and connected visual knowledge framework. No goal, level, time, energy, route-adjustment form, or pre-test is required.
6. Select **Start one focused step**. Confirm that the first concept explanation appears immediately with its prerequisite → current → next relationship, concrete example, memory anchor, and lightweight source disclosure.
7. Click several map nodes to inspect how each idea fits the framework, open the secondary Tutor support if useful, then choose either **Check this concept · 3 quick questions** or **Explain it yourself · 1 response**.
8. Submit an answer and review the immediate correct/not-quite result, answer check, and concise explanation.
9. Select **Keep going**. StartOne records factual `LearningEvidence`, requests exactly one Adaptive Planning Agent action and applies that safe action automatically. If a validated gap blocks learning, the only exceptional action is to reopen upload for more learner-supplied material.
10. Pause or refresh at any point to verify exact recovery.

Expected result: every map node is keyboard-clickable and reveals its relationship without changing the route; the Session status rail is absent; explanations show source provenance; Quiz contains exactly three questions and uses only a quiet origin line rather than file-location rows; `LearningEvidence` contains observations only; and no Agent decision screen interrupts momentum. Safe next actions apply automatically, and uploaded material remains the only learning source.

## Uploaded-material-only verification

The final learner UI intentionally contains no evaluator controls, web-search permission or candidate-link screen. Automated tests use the one-source fixture to prove that a validated blocking gap can only produce `request_more_material` with `required_tool=open_material_upload`. It preserves the current concept and reuses the normal upload area.

Expected result: Tutor, map, practice, feedback and Agent calls receive no network tool. The learner may upload more material or continue the current scope without losing progress.

## Reset and privacy

No sign-in is required. Anonymous workspaces are isolated with an HTTP-only same-site cookie. Use **Settings → Delete all data** to reset the browser workspace. The public free-tier app may also reset after a service restart.

## GPT-5.6 path

The public product uses the server-side OpenAI Responses API, strict Pydantic Structured Outputs, and bounded function calling for the Agent. No learning call receives a network tool, and the deployment secret is never exposed to the anonymous browser workspace. Deterministic fixtures remain internal to automated tests.
