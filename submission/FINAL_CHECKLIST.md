# OpenAI Build Week submission checklist

Official deadline: July 21, 2026 at 5:00 PM Pacific Time.

## Eligibility and project

- [ ] Entrant and every team member meet the official eligibility rules.
- [x] Category selected: Education.
- [x] Project was built during the submission period; dated Git history and the Codex build log distinguish the original specification baseline from implementation.
- [x] Project uses Codex and has an implemented GPT-5.6 Responses API path.
- [x] Third-party Python dependencies are used under their licenses; repository code is MIT licensed.

## Repository and testing

- [x] Push the final Git history to the public judge-accessible repository at https://github.com/jiangggqr/startone.
- [x] Keep the MIT-licensed repository public through judging.
- [x] English README includes installation, sample data, internal deterministic tests, Codex collaboration, human decisions, and GPT-5.6 responsibilities.
- [x] The learner UI contains no mode/evaluator controls; deterministic fixtures remain internal tests.
- [x] Automated tests, dependency check, secret scan, responsive browser flow, and security headers are verified.
- [x] Complete and record one live GPT-5.6 core-flow smoke test with a server-side key; verify that learning calls expose no network tool.

## Public app

- [x] Deploy the GPT-5.6 product to https://startone-learning.onrender.com with the key stored only as a Render secret.
- [x] Verify `/api/health` and the upload → real map → explanation → three-question Quiz → feedback → automatic next-concept path on that exact URL.
- [x] Confirm judges need no login, payment, personal API key, or rebuild.
- [x] Keep the public Render service available through the judging period ending August 5, 2026 at 5:00 PM Pacific Time.
- [x] Replace the public demo placeholder in submission copy.

## Video

- [ ] Record the English demo using `submission/DEMO_VIDEO_SCRIPT.md`.
- [ ] Confirm final duration is under 3:00.
- [ ] Confirm audio explains both Codex and GPT-5.6 usage.
- [ ] Remove keys, personal data, private tabs, unauthorized trademarks, music, and copyrighted material.
- [ ] Upload as a public YouTube video and verify in a signed-out window.
- [ ] Replace `YOUTUBE_URL_PENDING` in submission copy.

## Devpost

- [x] English project description is drafted.
- [x] Codex `/feedback` Session ID: `019f7ff7-6b6a-74d1-98b2-2f895e28bbce`.
- [x] Replace the repository placeholder in submission copy.
- [ ] Add the public app, repository, and public YouTube links to the form.
- [ ] Review every field against the official rules and preview the final project page.
- [ ] Submit before the deadline only after the entrant confirms the final public action.
