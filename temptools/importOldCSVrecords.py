import csv
import sqlite3
import os
from datetime import datetime

# Database path - using the same path as the main application
DB_PATH = os.getenv('CPUTRACKER_DB_PATH', 'cputracker.db')

def get_db():
    """Create a database connection"""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def determine_result(platform_test_code, destination):
    """Determine the result based on platform test code and destination"""
    if platform_test_code == "999999":
        return "NFF"
    elif "Scrap: Return to ODM for Scrap" in str(destination):
        return "VM/PPS"
    else:
        return "VF"

def process_csv():
    """Process the CSV file and import records to the database"""
    csv_path = os.path.join('temp', 'ExportMarch27th2025.csv')
    db = get_db()
    cursor = db.cursor()

    # Get existing serial numbers from the database
    cursor.execute('SELECT serial_number FROM UNITS')
    existing_serials = {row['serial_number'] for row in cursor.fetchall()}

    # Read the CSV file
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Group records by serial number
        records_by_serial = {}
        for row in reader:
            serial = row['APU/CPU/GPU/GPU Card Serial Number\n       or\nGPU QR Code1 (Identification Scan via Diag for Asics without SN)\n       or\nGPU Lot Number (non-Functional Asics without SN)']
            if serial not in records_by_serial:
                records_by_serial[serial] = []
            records_by_serial[serial].append(row)

        # Process each serial number
        for serial, records in records_by_serial.items():
            if serial in existing_serials:
                print(f"Skipping existing serial number: {serial}")
                continue

            # Find the most relevant record
            selected_record = None
            for record in records:
                # Skip Golden Unit records
                if record['Destination'] == 'Golden Unit':
                    continue
                
                # Skip records that require 2nd Platform Verification
                if record['Requires 2nd Platform Verification run'] == 'Yes':
                    continue
                
                selected_record = record
                break

            if not selected_record:
                print(f"No valid record found for serial number: {serial}")
                continue

            # Prepare data for insertion
            date_received = selected_record['Date Received by Operator']
            datecode = selected_record['Datecode \n(required for APU/CPU, leave blank for GPU)']
            part_number = selected_record['AMD_OPN']
            platform_test_code = selected_record['Platform Test Code 1']
            destination = selected_record['Destination']
            result = determine_result(platform_test_code, destination)

            # Insert the record
            try:
                cursor.execute('''
                    INSERT INTO UNITS (serial_number, part_number, datecode, test_result, date_added)
                    VALUES (?, ?, ?, ?, ?)
                ''', (serial, part_number, datecode, result, date_received))
                print(f"Added record for serial number: {serial}")
            except sqlite3.Error as e:
                print(f"Error inserting record for serial {serial}: {e}")

    # Commit changes and close connection
    db.commit()
    db.close()

if __name__ == '__main__':
    process_csv()
