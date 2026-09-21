FROM python:3.12-slim

WORKDIR /app

# Install dependencies required for healthchecks and basic operations
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch CPU directly since it might not be in requirements.txt
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy backend source
COPY backend/ ./

# Copy ml directory (which includes models, artifacts, inference)
COPY ml/ ./ml/

# Set up non-root user
RUN addgroup --system appgroup && adduser --system --group appuser \
    && mkdir -p /app/storage/uploads \
    && chown -R appuser:appgroup /app

USER appuser
ENV TORCH_HOME=/tmp

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
