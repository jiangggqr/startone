# Deployment guide

StartOne ships as one FastAPI process that serves both the API and the static Web App. The public judge deployment runs the real GPT-5.6 path. Credentials belong only in the deployment secret store and never in browser code, repository files, screenshots, or chat.

## Required public settings

```dotenv
STARTFRAME_MODE=real
OPENAI_API_KEY=configure-in-deployment-secret-store
STARTFRAME_HOST=0.0.0.0
STARTFRAME_SECURE_COOKIES=true
STARTFRAME_MAX_FILE_MB=20
STARTFRAME_MAX_FILES=5
STARTFRAME_MAX_SESSIONS_PER_WORKSPACE=20
STARTFRAME_MAX_SOURCES_PER_WORKSPACE=50
```

Configure `OPENAI_API_KEY` as a private deployment secret and set project budgets/rate limits in the OpenAI platform. The existing workspace quotas reduce accidental application-level abuse but are not a substitute for account-level spend controls. Deterministic fixtures are reserved for automated/local acceptance tests and are not a public learner mode.

## Render Blueprint

The repository includes `render.yaml` and a production Dockerfile.

1. Push this repository to GitHub or GitLab.
2. In Render, create a Blueprint from the repository.
3. Confirm the `startone-learning` web service and deploy it.
4. Add the private `OPENAI_API_KEY`, then open `/api/health` and confirm `status=ok`, `mode=real`, and `version=1.0.0`.
5. Complete the judge path in `submission/JUDGE_TESTING_GUIDE.md` on the public URL.

The Render free tier has an ephemeral filesystem. A restart can clear anonymous learning sessions and uploads, which is acceptable for resettable judging but not for durable production use. A production deployment should attach persistent storage or replace SQLite/file storage with managed persistent services.

## Docker

```bash
docker build -t startframe-agent .
docker run --rm -p 8000:8000 \
  -e STARTFRAME_MODE=real \
  -e OPENAI_API_KEY=your-server-side-secret \
  -e STARTFRAME_SECURE_COOKIES=false \
  startframe-agent
```

Open `http://127.0.0.1:8000/api/health` before testing the UI.

## Isolated real-model smoke test

Create a local `.env` that is never committed:

```dotenv
STARTFRAME_MODE=real
OPENAI_API_KEY=your-server-side-secret
STARTFRAME_OPENAI_MODEL=gpt-5.6-luna
STARTFRAME_SECURE_COOKIES=false
```

Restart the service, upload the included sample materials, and exercise knowledge-map generation, Tutor, practice feedback, an Agent decision, and the confirmed search path. Remove the key from the environment when verification is complete. Never paste it into chat, browser storage, screenshots, videos, logs, or Git.

For the isolated automated core-flow check used by the 1.0.0 release:

```bash
STARTFRAME_RUN_LIVE_SMOKE=1 python scripts/live_smoke.py
```

The runner uses temporary storage and does not print the key or generated learning content. Controlled real web-search request shape and citation filtering are verified separately by the automated contract suite.
