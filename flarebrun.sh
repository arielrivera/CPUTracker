#!/bin/zsh

CERT_DIR="./certs"
CERT_FILE="$CERT_DIR/localhost.crt"
KEY_FILE="$CERT_DIR/localhost.key"


# Stop and remove the existing containers
docker stop cputrackerapp nginx4cputrackapp
docker container rm cputrackerapp nginx4cputrackapp

# Path to the database file on the host machine
DATABASE_PATH=$(pwd)/cputracker.db

# The folder that contains logs
TARGET_FOLDER="/Users/arivera/Downloads/processed_logs"

# Target folder exists or not, prompt or use temp folder
TEMP_FOLDER="/tmp/processed_logs"
if [ ! -d "$TARGET_FOLDER" ]; then
  echo "\nThe folder $TARGET_FOLDER does not exist."
  echo "---------------------------------------------"
  echo "| Please provide a valid folder path         |"
  echo "| or press Enter to use the temporary folder |"
  echo "---------------------------------------------"
  echo -n "Folder path: "
  read USER_FOLDER

  # If the user provides a folder, use it
  if [ -n "$USER_FOLDER" ]; then
    TARGET_FOLDER="$USER_FOLDER"
    # FUTURE: Implement user-provided path validation, foolproof it
    echo "Using provided folder: $TARGET_FOLDER"
  else
    # Use the temporary folder if no folder is provided
    TARGET_FOLDER="$TEMP_FOLDER"
    if [ ! -d "$TARGET_FOLDER" ]; then
      mkdir -p "$TARGET_FOLDER"
      echo "Created temporary folder: $TARGET_FOLDER"
    else
      echo "Using temporary folder: $TARGET_FOLDER"
    fi
  fi
fi

# Remove all images
docker rmi cputrackerapp_image nginx_image

# Build the Docker images
docker build -t cputrackerapp_image -f Dockerfile.flask .
docker build -t nginx_image -f Dockerfile.nginx .

# Create the network if it doesn't exist
if ! docker network ls | grep -q cputracker_network; then
  docker network create cputracker_network
fi

# Start the Flask container
docker run -d --name cputrackerapp --network cputracker_network -v "$DATABASE_PATH":/app/cputracker.db -v "$TARGET_FOLDER":/app/logs_folder cputrackerapp_image

# Start the Nginx container
docker run -d --name nginx4cputrackapp --network cputracker_network -p 80:80 -p 443:443 -v "$CERT_FILE":/etc/nginx/certs/localhost.crt -v "$KEY_FILE":/etc/nginx/certs/localhost.key nginx_image