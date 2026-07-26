#!/bin/bash
# Deployment automation script

set -e

ENVIRONMENT=${1:-staging}
APP_NAME=${2:-bot}

echo "Deploying $APP_NAME to $ENVIRONMENT..."

# Validate environment
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "Error: Environment must be 'staging' or 'production'"
    exit 1
fi

# Check for required files
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found"
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    echo "Error: docker-compose.yml not found"
    exit 1
fi

# Build and deploy
echo "Building Docker image..."
docker build -t $APP_NAME:$ENVIRONMENT .

echo "Stopping existing containers..."
docker-compose down

echo "Starting services..."
docker-compose up -d

echo "Checking health..."
sleep 10
docker-compose ps

echo "Deployment to $ENVIRONMENT complete!"
