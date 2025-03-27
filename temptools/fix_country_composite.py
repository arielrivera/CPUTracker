import sqlite3
import os
import csv

# Database path - using the same path as the main application
DB_PATH = os.getenv('CPUTRACKER_DB_PATH', os.path.join('database', 'cputracker.db'))

def get_db():
    """Create a database connection"""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def get_csv_data():
    """Read the CSV file and create a mapping of serial numbers to country and part number"""
    csv_path = os.path.join('temp', 'ExportMarch27th2025.csv')
    data_map = {}
    
    # Try different encodings
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(csv_path, 'r', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    serial = row['APU/CPU/GPU/GPU Card Serial Number\n       or\nGPU QR Code1 (Identification Scan via Diag for Asics without SN)\n       or\nGPU Lot Number (non-Functional Asics without SN)']
                    country = row['Country of Origin']
                    part_number = row['AMD_OPN']
                    data_map[serial] = {
                        'country': country,
                        'composite_snpn': f"{serial}_{part_number}"
                    }
                print(f"Successfully read CSV file with {encoding} encoding")
                break  # If we get here, the encoding worked
        except UnicodeDecodeError:
            continue  # Try next encoding
        except Exception as e:
            print(f"Error reading CSV with {encoding} encoding: {e}")
            continue
    
    return data_map

def fix_fields():
    """Fix the country and composite_snpn fields in the database for specific records"""
    db = get_db()
    cursor = db.cursor()

    # Get the CSV data mapping
    csv_data = get_csv_data()

    # Get only the records we need to fix (IDs 622-657)
    cursor.execute('SELECT id, serial_number FROM UNITS WHERE id BETWEEN 622 AND 657')
    records = cursor.fetchall()

    # Process each record
    for record in records:
        serial = record['serial_number']
        if serial in csv_data:
            try:
                cursor.execute('''
                    UPDATE UNITS 
                    SET country = ?,
                        composite_snpn = ?
                    WHERE id = ?
                ''', (csv_data[serial]['country'], 
                      csv_data[serial]['composite_snpn'],
                      record['id']))
                print(f"Updated record {record['id']} (SN: {serial}):")
                print(f"  Country: {csv_data[serial]['country']}")
                print(f"  Composite SN/PN: {csv_data[serial]['composite_snpn']}")
            except sqlite3.Error as e:
                print(f"Error updating record {record['id']}: {e}")
        else:
            print(f"Warning: No CSV data found for serial number {serial}")

    # Commit changes and close connection
    db.commit()
    db.close()

if __name__ == '__main__':
    fix_fields() 