#!/bin/bash

# Stop and remove all containers
echo "Stopping and removing all containers..."
docker rm -f $(docker ps -a -q)

# Remove all images
echo "Removing all images..."
docker rmi -f $(docker images -q)

# Remove all volumes
echo "Removing all volumes..."
docker volume rm $(docker volume ls -q)

# Remove all build caches
echo "Removing all build caches..."
docker builder prune -f

echo "Cleanup completed!"
