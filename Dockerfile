# Build frontend
FROM node:18-alpine as frontend-builder
WORKDIR /frontend
COPY viz/package*.json ./
RUN npm install
COPY viz/ .
RUN npm run generate

# Build Python dependencies
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    nginx \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy only pyproject.toml first
COPY pyproject.toml .

# Generate poetry.lock and install dependencies
RUN poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install --no-interaction --no-ansi --no-root && \
    python3 -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Copy built frontend from builder
COPY --from=frontend-builder /frontend/.output/public /app/static

# Configure nginx
COPY nginx.conf /etc/nginx/nginx.conf
RUN mkdir -p /var/log/nginx /var/cache/nginx && \
    chown -R www-data:www-data /var/log/nginx /var/cache/nginx

# Create necessary directories
RUN mkdir -p txt_data json_data && \
    chown -R www-data:www-data /app/static /app/json_data

# Start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80
CMD ["/start.sh"] 