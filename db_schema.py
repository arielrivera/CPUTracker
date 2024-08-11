import sqlite3

# Connect to the database
conn = sqlite3.connect('cputracker.db')
cursor = conn.cursor()

# Create the LOGS table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS LOGS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name VARCHAR(100),
        serial_number VARCHAR(20) NOT NULL,
        host_status TEXT,
        csv_file_name VARCHAR(255),
        csv_file_content TEXT
    );
''')

# Create the UNITS table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS UNITS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
        date_last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
        serial_number VARCHAR(20) UNIQUE NOT NULL ,
        part_number VARCHAR(20),
        datecode VARCHAR(10),
        country VARCHAR(15),
        composite_snpn VARCHAR(30),
        test_result VARCHAR(10) DEFAULT 'NONE'
    );
''')

# Create the AUDIT table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS AUDIT (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serial_number VARCHAR(20) NOT NULL,
        date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        changes TEXT
    );
''')

# Create the AUDIT table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS PARTS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_number VARCHAR(20) NOT NULL,
        date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        enabled BOOLEAN DEFAULT TRUE
    );
''')

# Commit the changes
conn.commit()

# Close the connection
conn.close()
