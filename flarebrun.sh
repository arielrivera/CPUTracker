#!/bin/zsh

#Stop the container
docker stop cputrackerapp
#Remove the container
docker container rm cputrackerapp

#  path to the database file on the host machine
DATABASE_PATH=$(pwd)/cputracker.db

#  the folder that contains logs
TARGET_FOLDER="/Users/arivera/Downloads/processed_logs"
# LINK_NAME="LOGS_FOLDER"
# #  symbolic link in the current folder
# ln -s /Users/arivera/Downloads/processed_logs LOGS_FOLDER
# ln -s "$TARGET_FOLDER" "$LINK_NAME"


#  target folder exists or not , prompt or use temp folder
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
    # implement user provided path validation, fool proof it
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

#Remove all images 
docker rmi cputrackerapp_image
docker build -t cputrackerapp_image .

# Start the container

docker run --name cputrackerapp -v "$DATABASE_PATH":/app/cputracker.db -v "$TARGET_FOLDER":/app/logs_folder -p 5001:5001 cputrackerapp_image