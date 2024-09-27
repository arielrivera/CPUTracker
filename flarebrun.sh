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
    if [ ! -d "$TARGET_FOLDER" ]; then
      echo "The provided folder does not exist or is not valid."
      TARGET_FOLDER="$TEMP_FOLDER"
    else
      echo "Using provided folder: $TARGET_FOLDER"
    fi
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

# Export the TARGET_FOLDER environment variable
export TARGET_FOLDER="$TARGET_FOLDER"
echo "TARGET_FOLDER=$TARGET_FOLDER" > .env

# Stop and remove the existing containers
docker compose -p proj_cputracker down

# Explicitly stop and remove any existing containers with the same name
docker rm -f cputrackerapp
docker rm -f nginx4cputrackapp

# Remove all images forcefully
docker rmi -f cputrackerapp_image
docker rmi -f nginx4cputracker_image

# Start the services using Docker Compose
docker compose -p proj_cputracker up -d