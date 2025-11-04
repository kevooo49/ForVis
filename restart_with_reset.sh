#!/bin/sh

# Navigate to the frontend directory
cd frontend

# Install project dependencies
npm install

# Build the frontend application
npm run build

# Navigate back to the root directory
cd ..

# Build and start the Docker containers
docker-compose up --build
