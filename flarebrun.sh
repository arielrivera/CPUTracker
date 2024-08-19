#!/bin/zsh

#Stop the container
docker stop cputrackerapp
#Remove the container
docker container rm cputrackerapp

# Define the path to the database file on the host machine
DATABASE_PATH=$(pwd)/cputracker.db

# Define the path to the folder you want to link to
TARGET_FOLDER="/Users/arivera/Downloads/processed_logs"
# LINK_NAME="LOGS_FOLDER"

# # Create a symbolic link in the current folder
# ln -s /Users/arivera/Downloads/processed_logs LOGS_FOLDER
# ln -s "$TARGET_FOLDER" "$LINK_NAME"

#Remove all images 
docker rmi cputrackerapp_image
docker build -t cputrackerapp_image .

# Start the container

docker run --name cputrackerapp -v "$DATABASE_PATH":/app/cputracker.db -v "$TARGET_FOLDER":/app/logs_folder -p 5001:5001 cputrackerapp_image