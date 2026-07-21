FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STARTFRAME_HOST=0.0.0.0 \
    STARTFRAME_PORT=8000

WORKDIR /app

RUN addgroup --system startframe && adduser --system --ingroup startframe startframe

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY --chown=startframe:startframe . .
RUN mkdir -p /app/instance/uploads && chown -R startframe:startframe /app/instance

USER startframe

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import os, urllib.request; port=os.getenv('PORT', os.getenv('STARTFRAME_PORT', '8000')); urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health', timeout=4)"

CMD ["sh", "-c", "python -m uvicorn app.main:app --host ${STARTFRAME_HOST:-0.0.0.0} --port ${PORT:-${STARTFRAME_PORT:-8000}}"]
