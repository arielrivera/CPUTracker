@echo off
setlocal

:: Stop and remove the container
docker stop cputrackerapp
docker container rm cputrackerapp

:: Delete and rebuild image(s)
docker rmi cputrackerapp_image
docker build -t cputrackerapp_image .

@REM :: Define paths
set "DATABASE_PATH=%cd%\cputracker.db"
set "TARGET_FOLDER=C:\Users\OSVHo\OneDrive - Triple Crown AES\Documents\OSV Template\Processed
set "TEMP_FOLDER=%TEMP%\temp_folder"

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

REM Create the folder if it doesn't exist
if not exist "%TARGET_FOLDER%" (
    mkdir "%TARGET_FOLDER%"
    echo Created temporary folder: %TARGET_FOLDER%
) else (
    echo Using folder: %TARGET_FOLDER%
)

:: Start the container
docker run --name cputrackerapp -v "%DATABASE_PATH%:/app/cputracker.db" -v "%TARGET_FOLDER%:/app/logs_folder" -p 5001:5001 cputrackerapp_image

endlocal
@echo on