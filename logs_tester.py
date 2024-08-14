# from flask import Flask, g, request, render_template, Response, jsonify, session, redirect, url_for, make_response, flash
# from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 , os, shutil, sqlite3, py7zr
# from flask_bootstrap import Bootstrap
from datetime import datetime

# Database connection
_db = None

def get_db():
    global _db  # Declare _db as a global variable
    if db is None:
        _db = sqlite3.connect('cputracker.db')
        _db.row_factory = sqlite3.Row  # Enable accessing columns by name
        return _db


def write_to_audit(message, audit_type):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO AUDIT (message, audit_type, date_time)
            VALUES (?, ?, ?)
        ''', (message, audit_type, datetime.now()))
        db.commit()
        db.close()


# --------- LOGS AREA START
# Global variable to ensure the process runs only once
process_running = False

# @app.route('/start_process', methods=['POST'])
# def start_process_route():
#     data = request.get_json()
#     mode = data.get('mode', 'new-files')
#     start_process(mode)
#     return jsonify({"message": "Process started in mode: " + mode})

# @app.route('/stop_process', methods=['POST'])
# def stop_process_route():
#     stop_process()
#     return jsonify({"message": "Process stopped."})

# Moved from abandoned extra py file 
#
def get_serial_number(file_name):
    write_to_audit("get_serial_number,  file: {file_name}", '7zlogfiles')
    parts = file_name.split('_')
    if len(parts) > 2:
        return parts[1]
    return None

def process_file(file_path, temp_folder, db):
    write_to_audit("process_file,  file_path: {file_path}  temp_folder: {temp_folder}", '7zlogfiles')
    file_name = os.path.basename(file_path)
    serial_number = get_serial_number(file_name)
    if not serial_number:
        write_to_audit("process_file,  Invalid file name format.", '7zlogfiles')
        return "Invalid file name format."

    # Copy file to temp folder
    temp_file_path = os.path.join(temp_folder, file_name)
    shutil.copy(file_path, temp_file_path)
    write_to_audit("process_file,  temp_file_path: {temp_file_path}", '7zlogfiles')
    try:
        with py7zr.SevenZipFile(temp_file_path, mode='r') as archive:
            archive.extractall(path=temp_folder)
        write_to_audit("process_file, Extraction of completed successfully.", '7zlogfiles')
        
    except FileNotFoundError:
        write_to_audit("Error: File {temp_file_path} not found.", '7zlogfiles')
    except py7zr.exceptions.Bad7zFile:
        write_to_audit("Error: {temp_file_path} is not a valid 7z file.", '7zlogfiles')
    except Exception as e:
        write_to_audit("An error occurred: {str(e)}", '7zlogfiles')

    # Read Host_Status.txt
    host_status_path = os.path.join(temp_folder, 'Host_Status.txt')
    host_status = None
    if os.path.exists(host_status_path):
        with open(host_status_path, 'r') as file:
            host_status = file.read()

    # Read CSV file
    csv_file_name = None
    csv_file_content = None
    for file in os.listdir(temp_folder):
        if file.startswith(serial_number) and file.endswith('.csv'):
            csv_file_name = file
            with open(os.path.join(temp_folder, file), 'r') as csv_file:
                csv_file_content = csv_file.read()
            break

    # Store data in the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
            INSERT INTO LOGS (file_name, serial_number, host_status, csv_file_name, csv_file_content) 
            VALUES (?, ?, ?, ?, ?)
        """, ('example.7z', '12345', 'active', 'example.csv', 'csv content here'))
    db.commit()

    # Clean up temp folder
    shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    return "Processed file: {file_name}"

def process_logs(mode):
    global process_running
    write_to_audit('Running function process_logs.', '7zlogfiles')
    if process_running:
        return "Process is already running."
    process_running = True

    logs_folder = "/Users/arivera/Downloads/processed_logs/"
    temp_folder = "//Users/arivera/Downloads/processed_logs/tmp/"
    db = get_db()

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    files = [os.path.join(logs_folder, f) for f in os.listdir(logs_folder) if f.endswith('.7z')]
    if mode == "new-files":
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    else:
        files.sort(key=lambda x: os.path.getctime(x))

    for file in files:
        result = process_file(file, temp_folder, db)
        write_to_audit('process_logs->process_file: {result}.', '7zlogfiles')
        print(result)  # This would be sent to the web interface in a real application

    process_running = False
    return "Process completed."


# def stop_process():
#     global process_running
#     process_running = False 

# def run_process_logs_in_context():
#     with app.app_context():
#         process_logs()


if __name__ == '__main__':
    process_logs("new-files")
