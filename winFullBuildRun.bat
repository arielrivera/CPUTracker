@echo off

:: Stop the container
docker stop cputrackerapp

:: Remove the container
docker container rm cputrackerapp

:: Define the path to the database file on the host machine
set DATABASE_PATH=%cd%\cputracker.db

:: Define the path to the folder you want to link to
set TARGET_FOLDER=%USERPROFILE%\Documents\tester_logs
set LINK_NAME=LOGS_FOLDER

:: Create a symbolic link in the current folder
mklink /J "%LINK_NAME%" "%TARGET_FOLDER%"

:: Remove all images
docker rmi cputrackerapp_image
docker build -t cputrackerapp_image .

:: Start the container
docker run --name cputrackerapp -v "%DATABASE_PATH%:/app/cputracker.db" -v "%cd%\%LINK_NAME%:/app/logs_folder" -p 5001:5001 cputrackerapp_image

@echo on
