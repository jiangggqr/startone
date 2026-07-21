# StartFrame Agent — judge testing guide

## Fastest path: no key required

The public deployment runs in deterministic **Demo mode** and needs no account or API key.

1. Open the public Demo URL.
2. Select **Upload material and start a session**.
3. Select **Load standard Demo** to add `transformer_notes.md` and `matrix_prerequisite.md`.
4. Enter a learning goal, confirm setup, review source coverage, and generate the learning map.
5. Confirm the route and complete the short start action.
6. In the focus workspace, open Tutor, then try a Quiz or free recall.
7. Submit an answer, review the five-part feedback, and optionally complete a targeted remedial exercise.
8. Finish the feedback boundary to create factual `LearningEvidence`.
9. Ask the Adaptive Planning Agent for one next action; inspect its reason and penalty-free alternatives.
10. Pause or refresh at any point to verify exact recovery.

Expected result: every explanation and activity shows `uploaded`, `external`, or `AI supplemental` origin; `LearningEvidence` contains observations only; the Agent presents one global action and never teaches or grades.

## Controlled-search path

1. Start a fresh session and select **Load controlled-search Demo**.
2. Confirm that only `transformer_notes.md` is loaded and enable **Allow search suggestions for confirmed source gaps** during setup.
3. Generate coverage and the route. The source review names the missing dot-product prerequisite.
4. On the active concept, use Tutor to ask about the missing dot-product definition, then complete a not-yet-mastered Quiz or recall and finish feedback.
5. Run the Agent. It may select only one `request_search` action, and no search has run yet.
6. Accept the action. On the separate confirmation view, inspect all four gates and confirm the exact scope.
7. Execute Demo search, inspect three cited and visibly labeled external candidates, then select one or ignore all without penalty.

Expected result: search cannot execute unless session permission, a server-validated named gap, an accepted Agent request, and this exact user confirmation are all present.

## Reset and privacy

No sign-in is required. Anonymous workspaces are isolated with an HTTP-only same-site cookie. Use **Settings → Delete all data** to reset the browser workspace. The public free-tier Demo may also reset after a service restart.

## Real GPT-5.6 path

The repository includes a separate real mode using the server-side OpenAI Responses API, strict Pydantic Structured Outputs, bounded function calling for the Agent, and required `web_search` only after the four gates. A key is intentionally not exposed on the public anonymous Demo. See `DEPLOYMENT.md` for the private smoke-test procedure.
