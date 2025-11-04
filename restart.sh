#!/bin/sh

# Stop and remove all running containers, networks, and volumes defined in the docker-compose file
docker-compose down

echo "Containers have been stopped and removed. DONE."

# Start the containers defined in the docker-compose file
docker-compose up

# Uncomment the line below to rebuild images before starting the containers
# docker-compose up --build
