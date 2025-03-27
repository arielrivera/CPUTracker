import sqlite3
import os
from datetime import datetime

# Database path - using the same path as the main application
DB_PATH = os.getenv('CPUTRACKER_DB_PATH', os.path.join('database', 'cputracker.db'))

def get_db():
    """Create a database connection"""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def convert_date(date_str):
    """Convert date from MM/DD/YYYY to YYYY-MM-DD format"""
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        # Format it to YYYY-MM-DD
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        print(f"Error converting date: {date_str}")
        return None

def fix_dates():
    """Fix the date format in the database for specific records"""
    db = get_db()
    cursor = db.cursor()

    # Get only the records we need to fix (IDs 622-657)
    cursor.execute('SELECT id, date_added FROM UNITS WHERE id BETWEEN 622 AND 657')
    records = cursor.fetchall()

    # Process each record
    for record in records:
        old_date = record['date_added']
        new_date = convert_date(old_date)
        
        if new_date:
            try:
                cursor.execute('''
                    UPDATE UNITS 
                    SET date_added = ? 
                    WHERE id = ?
                ''', (new_date, record['id']))
                print(f"Updated date for record {record['id']}: {old_date} -> {new_date}")
            except sqlite3.Error as e:
                print(f"Error updating record {record['id']}: {e}")

    # Commit changes and close connection
    db.commit()
    db.close()

if __name__ == '__main__':
    fix_dates() 