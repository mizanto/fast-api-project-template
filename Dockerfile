FROM python:3.12-slim AS builder

WORKDIR /app

# Builder stage: install production dependencies once, then copy into a minimal runtime image.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-slim AS production

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local
COPY . .

# Production runtime only: app code + prod deps (tests are not installed).
# Run as non-root for better container isolation.
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

