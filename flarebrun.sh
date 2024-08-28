#!/bin/zsh

CERT_DIR="./certs"
CERT_FILE="$CERT_DIR/localhost.crt"
KEY_FILE="$CERT_DIR/localhost.key"

# Path to the database file on the host machine
DATABASE_PATH=$(pwd)/cputracker.db

# The folder that contains your .7z logs
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
# ----------------------------------------------------------
#      Docker
# ----------------------------------------------------------

# Stop and remove the existing containers
if docker ps -a | grep -q cputrackerapp; then
  docker stop cputrackerapp
  docker container rm cputrackerapp
fi
if docker ps -a | grep -q nginx4cputrackapp; then
  docker stop nginx4cputrackapp
  docker container rm nginx4cputrackapp
fi

# Remove all images
if docker images | grep -q cputrackerapp_image; then
  docker rmi cputrackerapp_image
fi
if docker images | grep -q nginx_image; then
  docker rmi nginx_image
fi

# Build the images
docker build -t cputrackerapp_image -f Dockerfile.flask .
docker build --build-arg TARGETPLATFORM=arm64 -t nginx_image -f Dockerfile.nginx .

# Create the container network if it doesn't exist
if ! docker network ls | grep -q cputracker_network; then
  docker network create cputracker_network
fi

# Start the Flask container
docker run \
-d --name cputrackerapp \
--network cputracker_network \
-v "$DATABASE_PATH":/app/cputracker.db \
-v "$TARGET_FOLDER":/app/logs_folder \
cputrackerapp_image


# Start the Nginx container
docker run \
-d --name nginx4cputrackapp \
--network cputracker_network \
-p 80:80 -p 443:443 \
-v "$CERT_FILE":/etc/nginx/certs/localhost.crt \
-v "$KEY_FILE":/etc/nginx/certs/localhost.key \
nginx_image