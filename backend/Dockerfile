FROM python:3.12-slim

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch CPU directly since it might not be in requirements.txt
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy backend source
COPY backend/ ./

# Copy ml directory (which includes models, artifacts, inference)
# We will use .dockerignore to exclude heavy datasets
COPY ml/ ./ml/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
