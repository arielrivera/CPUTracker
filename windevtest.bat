@echo off
call conda activate cputracker
set FLASK_ENV=development
set DEV_DB_PATH=database\cputracker.db
python app.py