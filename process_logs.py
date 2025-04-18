import os, time
import shutil
import sqlite3
import py7zr
import datetime
# import zlib
# from alive_progress import alive_bar

#  writable directory
WRITABLE_TEMP_DIR = '/tmp/cputracker_temp'
process_running = False

def get_db():
    db = sqlite3.connect('/app/database/cputracker.db')
    db.row_factory = sqlite3.Row  # This allows us to access columns by name
    return db

def file_exists(file_name, db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(1) FROM LOGS WHERE file_name = ?", (file_name,))
    exists = cursor.fetchone()[0] > 0
    # print(f"File {file_name} exists in the database ?: {exists}")
    cursor.close()
    return exists

def get_serial_number(file_name):
    parts = file_name.split('_')
    if len(parts) > 2:
        return parts[1]
    return None

# def compress_text(text):
#     return zlib.compress(text.encode('utf-8'))

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


    # Extract datetime assuming format is 100-000000933_9LN1136S20020_999999_AMD-HC-OSV-HTX0_SCR_YYYYMMDD_HHMMSS.7z
    date_time_str = temp_file_path.split('_')[-2] + temp_file_path.split('_')[-1].split('.')[0]  # Correct extraction
    lkt_datetime = datetime.datetime.strptime(date_time_str, '%Y%m%d%H%M%S')            
    print(f"lkt_datetime: {lkt_datetime}")
    # Update the lkt_datetime field in the UNITS table
    if lkt_datetime:
        update_lkt_datetime(db_conn, serial_number, lkt_datetime)
    

    # Extract test_code from the 3rd position
    test_code=''
    test_code = temp_file_path.split('_')[3]
    print(f"Test_code: {test_code}")


    # Read Host_Status.txt
    host_status_path = os.path.join(temp_folder, 'Host_Status.txt')
    print(f"Host status file path: {host_status_path}")
    host_status = None
    if os.path.exists(host_status_path):
        with open(host_status_path, 'r') as file:
            host_status = file.read()
        # print(f"\nCompressing text before inserting into db\n")
        # host_status = compress_text(host_status)

    # Read CSV file
    csv_file_name = None
    csv_file_content = None
    lkt_datetime = None
    files = [os.path.join(temp_folder, f) for f in os.listdir(temp_folder) if f.endswith('.csv')]
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    for file in files:
        if file.startswith(serial_number):
            csv_file_name = os.path.basename(file)
            with open(file, 'r') as csv_file:
                csv_file_content = csv_file.read()
                # print(f"\nCompressing text before inserting into db\n")
                # csv_file_content = compress_text(csv_file_content)
                # Extract date and time from the file name
            break
            

    # Store data in the database
    cursor = db_conn.cursor()
    current_timestamp = datetime.datetime.now()

    cursor.execute("""
    INSERT INTO LOGS (file_name, serial_number, host_status, csv_file_name, csv_file_content, date_added, test_code) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (file_name, serial_number, host_status, csv_file_name, csv_file_content, current_timestamp, test_code))

    db_conn.commit()

    # Clean up temp folder
    for file in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    os.makedirs(temp_folder, exist_ok=True)  #Shouldn't need this, but just in case

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
    print(f"Logs folder: {logs_folder}")
    print(f"Temp folder: {temp_folder}")


    if not os.path.exists(temp_folder):
        print(f"Temp folder not found, creating {temp_folder}")
        os.makedirs(temp_folder)
        # validate if it worked or not in the future

    files = [os.path.join(logs_folder, f) for f in os.listdir(logs_folder) if f.endswith('.7z')]
    if mode == "new-files":
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    else:
        files.sort(key=lambda x: os.path.getctime(x))

    if not files:
        print("No valid files found in the folder.\nStopping the process.")
        return "Process completed."
    
    for file in files:
        process_file(file, temp_folder, db_conn)

    # total_items = len(files)
    # process_file(file, temp_folder, db_conn)
    # with alive_bar(total_items, title='Processing', spinner='dots_waves', bar='smooth') as bar:
    #     for file in files:
    #         process_file(file, temp_folder, db_conn)
    #         bar() 


    process_running = False
    return "Process completed."

def start_process(mode):
    print('Starting process...')
    process_logs(mode)

def stop_process():
    global process_running
    process_running = False


def update_lkt_datetime(db_conn, serial_number, lkt_datetime):
    cursor = db_conn.cursor()
    cursor.execute("""
        UPDATE UNITS
        SET lkt_datetime = ?
        WHERE serial_number = ?
    """, (lkt_datetime, serial_number))
    db_conn.commit()

if __name__ == '__main__':
    start_process("new-files")