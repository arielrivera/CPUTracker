import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('cputracker.db')
cursor = conn.cursor()

# Fetch all records from the UNITS table
cursor.execute('SELECT serial_number, composite_snpn FROM UNITS')
rows = cursor.fetchall()

# Iterate through each record
for row in rows:
    serial_number = row[0]
    composite_snpn = row[1]
    
    # Split the composite_snpn value and get the part after the underscore
    part_number = composite_snpn.split('_')[1] if '_' in composite_snpn else ''
    
    # Update the part_number field for the same row
    cursor.execute('UPDATE UNITS SET part_number = ? WHERE serial_number = ?', (part_number, serial_number))

# Commit the changes and close the connection
conn.commit()
conn.close()