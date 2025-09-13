# backend/Dockerfile
FROM python:3.11-slim

ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install system deps needed for pillow, compiling wheels, etc.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libjpeg-dev \
    libz-dev \
    libpng-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# copy requirements list and install
COPY backend/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# default project layout: mount your host ./backend as /app/backend in docker-compose
# Copy a fallback so image can run even without volume (optional)
COPY backend /app/backend

ENV PYTHONUNBUFFERED=1
ENV REDIS_URL=redis://redis:6379
ENV BASE_URL=http://127.0.0.1:8000

EXPOSE 8000

# default command is uvicorn; worker container will override command in docker-compose
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
