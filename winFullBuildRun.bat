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

REM Export the TARGET_FOLDER environment variable
set "TARGET_FOLDER=%TARGET_FOLDER%"
set "TARGET_FOLDER=%TARGET_FOLDER%" > .env

REM Stop and remove the existing containers
docker-compose -p proj_cputracker down

REM Explicitly stop and remove any existing containers with the same name
docker rm -f cputrackerapp
docker rm -f nginx4cputrackapp

REM Remove all images forcefully
docker rmi -f cputrackerapp_image
docker rmi -f nginx4cputracker_image

REM Start the services using Docker Compose
docker-compose -p proj_cputracker up -d

endlocal
@echo on