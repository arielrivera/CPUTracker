#!/bin/zsh
#Stop the container
docker stop cputrackerapp
#Remove the container
docker container rm cputrackerapp

# Define the path to the database file on the host machine
DATABASE_PATH=$(pwd)/cputracker.db

#Remove all images 
docker rmi cputrackerapp_image
docker build -t cputrackerapp_image .
#run a container with name cputrackerapp using ports based in the image named my-streamlit-app
#docker run -d --name cputrackerapp -e DATABASE_PATH=/app/cputracker.db -p 8501:8501 cputrackerapp_image
#docker run -d --name cputrackerapp -e DATABASE_PATH=/app/cputracker.db -p 8501:8501 cputrackerapp_image

#docker run --name cputrackerapp -v "$DATABASE_PATH":/app/cputracker.db -p 8501:8501 cputrackerapp_image

#docker run -d -p 5000:5000 -v /path/to/your/logs/folder:/app/logs cpu-tracker
docker run --name cputrackerapp -v "$DATABASE_PATH":/app/cputracker.db -p 5001:5001 cputrackerapp_image 
