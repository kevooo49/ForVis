#!/bin/sh

# Remove the existing frontend container forcefully
docker rm forvis_frontend_1 --force

# Remove the existing frontend Docker image forcefully
docker rmi forvis_frontend:latest --force

# Navigate to the frontend directory
cd frontend

# Build the frontend application
npm run build

# Navigate back to the root directory
cd ..

# Start the containers defined in the docker-compose file
docker-compose up
