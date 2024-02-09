#!/bin/bash

# Initial check for Docker installation
if ! command -v docker &> /dev/null; then
    echo "Docker could not be found. Please install Docker."
    exit 1
fi

# Define your application's Docker image name
IMAGE_NAME="audit_log_service_image"

# Define your container name
CONTAINER_NAME="audit_log_service"

# The directory where your Dockerfile and application code reside
APP_DIR="/"

# Update your packages
sudo apt-get update && sudo apt-get upgrade

# Build the Docker image
echo "Building Docker image..."
if ! docker build -t "$IMAGE_NAME" .; then
    echo "--------------------------- Failed to build Docker image. Please check the logs above for any errors."
    exit 1
fi

# Check if a container with the same name already exists
if [ "$(docker ps -aq -f name=^${CONTAINER_NAME}$)" ]; then
    # Stop and remove the existing container
    echo "################################################  An existing container was found. Stopping and removing..."
    if ! docker stop "$CONTAINER_NAME"; then
        echo "--------------------------- Failed to stop the existing container. Please check the logs above for any errors."
        exit 1
    fi
    if ! docker rm "$CONTAINER_NAME"; then
        echo "--------------------------- Failed to remove the existing container. Please check the logs above for any errors."
        exit 1
    fi
fi

# Run the Docker container from the image
echo "Deploying the application..."
if ! docker run -d --name "$CONTAINER_NAME" -p 8000:8000 "$IMAGE_NAME"; then
    echo "--------------------------- Failed to start the application. Please check the logs above for any errors."
    exit 1
fi

echo "-------------------------------------------------------- Deployment completed. The application is now running."
echo "------------- Get access token here http://127.0.0.1:8000/access-token?valid_minutes=1800 "
