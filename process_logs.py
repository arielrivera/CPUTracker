import os
import shutil
import sqlite3
import py7zr
import datetime

# Define a writable directory
WRITABLE_TEMP_DIR = '/tmp/cputracker_temp'
# Global variable to ensure the process runs only once
process_running = False

def get_db():
    db = sqlite3.connect('cputracker.db')
    db.row_factory = sqlite3.Row  # This allows us to access columns by name
    return db

def file_exists(file_name, db_conn):
    print(f"Checking if file {file_name} exists in the database.")
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(1) FROM LOGS WHERE file_name = ?", (file_name,))
    exists = cursor.fetchone()[0] > 0
    print(f"File {file_name} exists in the database ?: {exists}")
    cursor.close()
    return exists

def get_serial_number(file_name):
    parts = file_name.split('_')
    if len(parts) > 2:
        return parts[1]
    return None

def process_file(file_path, temp_folder, db_conn):
    file_name = os.path.basename(file_path)
    print(f"Working with file: {file_name}")
    if(file_exists(file_name, db_conn)):
        print(f"File {file_name} already processed.\n")
        return f"File {file_name} already processed."
    serial_number = get_serial_number(file_name)
    print(f"Serial number: {serial_number}")
    if not serial_number:
        return "Invalid file name format."

    # Copy file to temp folder
    temp_file_path = os.path.join(temp_folder, file_name)
    print(f"Temp file path: {temp_file_path}")
    shutil.copy(file_path, temp_file_path)
    print(f"File copied to temp folder.")
    try:
        with py7zr.SevenZipFile(temp_file_path, mode='r') as archive:
            archive.extractall(path=temp_folder)
        print(f"Extraction of {file_name} completed successfully.")
    except FileNotFoundError:
        print(f"Error: File {temp_file_path} not found.")
    except py7zr.exceptions.Bad7zFile:
        print(f"Error: {temp_file_path} is not a valid 7z file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # Read Host_Status.txt
    host_status_path = os.path.join(temp_folder, 'Host_Status.txt')
    print(f"Host status file path: {host_status_path}")
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
    cursor = db_conn.cursor()
    current_timestamp = datetime.datetime.now()
    cursor.execute("""
    INSERT INTO LOGS (file_name, serial_number, host_status, csv_file_name, csv_file_content, date_added) 
    VALUES (?, ?, ?, ?, ?, ?)
""", (file_name, serial_number, host_status, csv_file_name, csv_file_content, current_timestamp))

    db_conn.commit()

    # Clean up temp folder
    shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    return f"Processed file: {file_name}"

def process_logs(mode):
    global process_running
    print("Process started in process_logs.py.")
    if process_running:
        return "Process is already running."
    process_running = True

    # For macos, the logs folder is /var/logs_folder
    logs_folder = "LOGS_FOLDER"

    # For Windows, the logs folder is logs_folder
    logs_folder = "logs_folder"
    temp_folder = WRITABLE_TEMP_DIR
    db_conn = get_db()

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    files = [os.path.join(logs_folder, f) for f in os.listdir(logs_folder) if f.endswith('.7z')]
    if mode == "new-files":
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    else:
        files.sort(key=lambda x: os.path.getctime(x))

    for file in files:
        process_file(file, temp_folder, db_conn)

    process_running = False
    return "Process completed."

def start_process(mode):
    print('Starting process...')
    process_logs(mode)

def stop_process():
    global process_running
    process_running = False

if __name__ == '__main__':
    start_process("new-files")