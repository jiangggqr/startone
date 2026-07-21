# StartFrame Agent — judge testing guide

## Fastest product path

The public deployment needs no learner account. GPT-5.6 credentials stay on the server and never appear in the browser.

1. Open the public app URL.
2. Select **Upload material and start a session**.
3. Upload `sample_data/transformer_notes.md` and `sample_data/matrix_prerequisite.md`, or upload your own readable PDF, Markdown, or TXT file.
4. Confirm that both file status and the next action appear inside the upload panel, then select **Build my learning path**.
5. Review the AI-selected learning focus, knowledge framework, concept route, and grounded references. No setup form is required.
6. Confirm the route and complete the short starting response; this is the first baseline signal, not a graded test.
7. In the focus workspace, inspect the concept explanation, open Tutor, then try a Quiz or free recall.
8. Submit an answer, review the five-part feedback, and optionally complete a targeted remedial exercise.
9. Finish the feedback boundary to create factual `LearningEvidence`, then ask the Adaptive Planning Agent for one next action.
10. Pause or refresh at any point to verify exact recovery.

Expected result: every explanation and activity shows `uploaded`, `external`, or `AI supplemental` origin; `LearningEvidence` contains observations only; the Agent presents one global action and never teaches or grades.

## Controlled-search verification

The final learner UI intentionally contains no evaluator button or forced-search shortcut. Automated tests use the one-source fixture to prove that search execution rejects every request unless session permission, a server-validated named gap, an accepted Agent `request_search`, and exact user confirmation are all present. The video demonstrates the resulting confirmation and cited-source views through a prepared product session.

Expected result: search cannot execute unless session permission, a server-validated named gap, an accepted Agent request, and this exact user confirmation are all present.

## Reset and privacy

No sign-in is required. Anonymous workspaces are isolated with an HTTP-only same-site cookie. Use **Settings → Delete all data** to reset the browser workspace. The public free-tier app may also reset after a service restart.

## GPT-5.6 path

The public product uses the server-side OpenAI Responses API, strict Pydantic Structured Outputs, bounded function calling for the Agent, and required `web_search` only after the four gates. The deployment secret is never exposed to the anonymous browser workspace. Deterministic fixtures remain internal to automated tests.
