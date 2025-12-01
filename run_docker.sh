#!/bin/bash
# Run Docker container with environment variables

docker run -d \
  -p 8000:8000 \
  -e PORT=8000 \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_NAME=diabetes_tracker \
  -e DB_USER=postgres \
  -e DB_PASSWORD="${DB_PASSWORD:-}" \
  -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
  --name diabetes-tracker \
  diabetes_tracker:latest
