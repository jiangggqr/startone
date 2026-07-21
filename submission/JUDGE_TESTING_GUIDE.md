# StartFrame Agent — judge testing guide

## Fastest product path

The public deployment needs no learner account. GPT-5.6 credentials stay on the server and never appear in the browser.

1. Open the public app URL.
2. Select **Upload material and start learning**.
3. Upload `sample_data/transformer_notes.md` and `sample_data/matrix_prerequisite.md`, or upload your own readable PDF, Markdown, or TXT file.
4. Confirm that both file status and the next action appear inside the upload panel, then select **Build my learning path**.
5. Review the AI-selected learning focus, knowledge framework, concept route, and grounded references. No setup form is required.
6. Review the concise knowledge framework and click **Start learning the first concept**. Confirm that the explanation appears immediately, with no setup form or pre-test.
7. In the focus workspace, click several knowledge-framework nodes, inspect the concept explanation, open Tutor, then choose either the 3-question Multiple choice test or the 1-response Free recall test.
8. Submit an answer and review the immediate correct/not-quite result, answer check, and concise explanation.
9. Select Continue. StartFrame records factual `LearningEvidence` and requests the Adaptive Planning Agent automatically, then shows one concise next action.
10. Pause or refresh at any point to verify exact recovery.

Expected result: every map node is keyboard-clickable and reveals its relationship without changing the route; the Session status rail is absent; explanations show source provenance; Quiz contains exactly three questions and uses only a quiet origin line rather than file-location rows; `LearningEvidence` contains observations only; and the next-step screen presents one global action without alternative-path controls or system architecture.

## Controlled-search verification

The final learner UI intentionally contains no evaluator button or forced-search shortcut. Automated tests use the one-source fixture to prove that search execution rejects every request unless session permission, a server-validated named gap, an accepted Agent `request_search`, and exact user confirmation are all present. The video demonstrates the resulting confirmation and cited-source views through a prepared product session.

Expected result: search cannot execute unless session permission, a server-validated named gap, an accepted Agent request, and this exact user confirmation are all present.

## Reset and privacy

No sign-in is required. Anonymous workspaces are isolated with an HTTP-only same-site cookie. Use **Settings → Delete all data** to reset the browser workspace. The public free-tier app may also reset after a service restart.

## GPT-5.6 path

The public product uses the server-side OpenAI Responses API, strict Pydantic Structured Outputs, bounded function calling for the Agent, and required `web_search` only after the four gates. The deployment secret is never exposed to the anonymous browser workspace. Deterministic fixtures remain internal to automated tests.
