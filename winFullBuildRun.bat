@echo off
setlocal

@REM :: Define paths
set "DATABASE_PATH=%cd%\cputracker.db"
set "TARGET_FOLDER=C:\Users\OSVHo\OneDrive - Triple Crown AES\Documents\OSV Template\Processed"
set "TEMP_FOLDER=%TEMP%\temp_folder"
set "TARGETPLATFORM=windows/amd64"

set "CERT_DIR=C:\Users\OSVHo\Documents\CPUTracker\certs"
set "CERT_FILE=%CERT_DIR%\localhost.crt"
set "KEY_FILE=%CERT_DIR%\localhost.key"

REM Checking if TARGET_FOLDER exists
if not exist "%TARGET_FOLDER%" (
    echo.
    echo The folder %TARGET_FOLDER% does not exist.
    echo "---------------------------------------------"
    echo "| Please provide a valid folder path         |"
    echo "| or press Enter to use the temporary folder |"
    echo "---------------------------------------------"
    echo DEBUG: Before user input
    set /p USER_FOLDER=Folder path: 
    echo DEBUG: After user input, USER_FOLDER=%USER_FOLDER%

    REM If the user provides a folder, use it
    if not "%USER_FOLDER%"=="" (
        set "TARGET_FOLDER=%USER_FOLDER%"
        REM Validate the provided folder
        if not exist "%TARGET_FOLDER%" (
            echo The provided folder does not exist or is not valid.
            set "TARGET_FOLDER=%TEMP_FOLDER%"
        ) else (
            echo Using provided folder: %TARGET_FOLDER%
        )
    ) else (
        REM Use a temporary folder if no folder is provided
        set "TARGET_FOLDER=%TEMP_FOLDER%"
    )
)

REM Create the container network if it doesn't exist
docker network ls | findstr cputracker_network >nul
if %errorlevel% neq 0 (
    docker network create cputracker_network
)

REM Stop and remove the existing containers
docker ps -a | findstr cputrackerapp >nul
if %errorlevel% equ 0 (
    docker stop cputrackerapp
    docker container rm cputrackerapp
)

docker ps -a | findstr nginx4cputrackapp >nul
if %errorlevel% equ 0 (
    docker stop nginx4cputrackapp
    docker container rm nginx4cputrackapp
)

REM Remove all images
docker images | findstr cputrackerapp_image >nul
if %errorlevel% equ 0 (
    docker rmi cputrackerapp_image
)

docker images | findstr nginx_image >nul
if %errorlevel% equ 0 (
    docker rmi nginx_image
)

REM Build the cputrackerapp image
docker build -t cputrackerapp_image -f Dockerfile.flask .


REM Start the cputrackerapp Flask container 
docker run ^
-d --name cputrackerapp ^
--network cputracker_network ^
-v "%DATABASE_PATH%":/app/cputracker.db ^
-v "%TARGET_FOLDER%":/app/logs_folder ^
cputrackerapp_image


REM Build the nginx_image image
docker build --build-arg TARGETPLATFORM=amd64 -t nginx_image -f Dockerfile.nginx .
REM Start the Nginx container
docker run ^
--name nginx4cputrackapp ^
--network cputracker_network ^
-p 80:80 -p 443:443 ^
nginx_image
@REM -v "%CERT_FILE%":/etc/nginx/certs/localhost.crt ^
@REM -v "%KEY_FILE%":/etc/nginx/certs/localhost.key ^

endlocal
@echo on