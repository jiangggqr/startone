# Deployment guide

StartFrame Agent ships as one FastAPI process that serves both the API and the static Web App. The public judge deployment should run in deterministic Demo mode. Real GPT-5.6 credentials belong only in a private server environment used for the required live smoke test.

## Required public settings

```dotenv
STARTFRAME_MODE=demo
STARTFRAME_HOST=0.0.0.0
STARTFRAME_SECURE_COOKIES=true
STARTFRAME_MAX_FILE_MB=20
STARTFRAME_MAX_FILES=5
STARTFRAME_MAX_SESSIONS_PER_WORKSPACE=20
STARTFRAME_MAX_SOURCES_PER_WORKSPACE=50
```

Do not configure `OPENAI_API_KEY` on the public Demo service. This prevents anonymous visitors from spending model credits. The Demo still exposes every product boundary and uses visibly labeled deterministic fixtures.

## Render Blueprint

The repository includes `render.yaml` and a production Dockerfile.

1. Push this repository to GitHub or GitLab.
2. In Render, create a Blueprint from the repository.
3. Confirm the `startframe-agent` web service and deploy it.
4. Open `/api/health` and confirm `status=ok`, `mode=demo`, and `version=1.0.0`.
5. Complete the judge path in `submission/JUDGE_TESTING_GUIDE.md` on the public URL.

The Render free tier has an ephemeral filesystem. A restart can clear anonymous learning sessions and uploads, which is acceptable for the resettable judge Demo but not for durable production use. A production deployment should attach persistent storage or replace SQLite/file storage with managed persistent services.

## Docker

```bash
docker build -t startframe-agent .
docker run --rm -p 8000:8000 \
  -e STARTFRAME_MODE=demo \
  -e STARTFRAME_SECURE_COOKIES=false \
  startframe-agent
```

Open `http://127.0.0.1:8000/api/health` before testing the UI.

## Private real-model smoke test

Create a local `.env` that is never committed:

```dotenv
STARTFRAME_MODE=real
OPENAI_API_KEY=your-server-side-secret
STARTFRAME_OPENAI_MODEL=gpt-5.6
STARTFRAME_SECURE_COOKIES=false
```

Restart the service, upload the included sample materials, and exercise knowledge-map generation, Tutor, practice feedback, an Agent decision, and the confirmed search path. Remove the key from the environment when verification is complete. Never paste it into chat, browser storage, screenshots, videos, logs, or Git.

For the isolated automated core-flow check used by the 1.0.0 release:

```bash
STARTFRAME_RUN_LIVE_SMOKE=1 python scripts/live_smoke.py
```

The runner uses temporary storage and does not print the key or generated learning content. Controlled real web-search request shape and citation filtering are verified separately by the automated contract suite.
