# ═══════════════════════════════════════════════════════════════
# Alia — AI Legal Assistant for Côte d'Ivoire
# ═══════════════════════════════════════════════════════════════

FROM python:3.12-slim

# ── Prevent Python from writing .pyc files & buffer stdout/stderr ──
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.yaml .
COPY app.py .
COPY services/ ./services/
COPY pipeline/ ./pipeline/
COPY ui/ ./ui/
COPY utils/ ./utils/

RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/_stcore/health || exit 1

CMD streamlit run app.py \
    --server.port=${PORT:-8080} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.fileWatcherType=none \
    --client.showErrorDetails=false
