#!/bin/zsh
#Stop the container
docker stop cputrackerapp
#Remove the container
docker container rm cputrackerapp

# Define the path to your database file on the host machine
DATABASE_PATH="/Users/arielrivera/Documents/GitHub/CPUTracker/cputracker.db"

#Remove all images 
docker rmi cputrackerapp_image
docker build -t cputrackerapp_image .
#run a container with name cputrackerapp using ports based in the image named my-streamlit-app
docker run -d --name cputrackerapp -e DATABASE_PATH=/app/cputracker.db -p 8501:8501 cputrackerapp_image