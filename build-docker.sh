#!/bin/bash
# Build and run Buildozer in Docker

echo "Building Docker image for Buildozer Android build..."
docker compose -f docker-compose.buildozer.yml build --no-cache

echo ""
echo "Running Buildozer build inside Docker..."
docker compose -f docker-compose.buildozer.yml run --rm buildozer buildozer android debug

echo ""
echo "✓ Build complete. APK should be in ./bin/"
