#!/bin/bash
# Quick deployment script for AWS App Runner
# Usage: ./deploy.sh <aws-region> <ecr-repo-name> <aws-account-id>

set -e

REGION=${1:-us-east-1}
REPO_NAME=${2:-diabetes-tracker}
ACCOUNT_ID=${3}

if [ -z "$ACCOUNT_ID" ]; then
    echo "Usage: ./deploy.sh <aws-region> <ecr-repo-name> <aws-account-id>"
    echo "Example: ./deploy.sh us-east-1 diabetes-tracker 123456789012"
    exit 1
fi

ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}"

echo "Building Docker image..."
docker build -t ${REPO_NAME}:latest .

echo "Tagging image..."
docker tag ${REPO_NAME}:latest ${ECR_URI}:latest

echo "Logging into ECR..."
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}

echo "Pushing image to ECR..."
docker push ${ECR_URI}:latest

echo "Deployment complete!"
echo "Image URI: ${ECR_URI}:latest"
echo ""
echo "Next steps:"
echo "1. Go to AWS App Runner console"
echo "2. Create/update service with image: ${ECR_URI}:latest"
echo "3. Set environment variables (DB_HOST, DB_PORT, etc.)"

