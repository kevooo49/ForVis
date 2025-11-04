#!/bin/sh

# Wait for RabbitMQ server to start
# Ensures RabbitMQ is up and ready before starting the Celery worker
sleep 10

# Change directory to the application source folder
cd /usr/src/app

# Run the Celery worker for the project
# - Uses the specified Celery configuration module (formulavis.celeryconf)
# - Processes tasks in the "default" queue
# - Assigns a worker name that includes the hostname for easier identification
su -m myuser -c "celery worker -A formulavis.celeryconf -Q default -n default@%h"
