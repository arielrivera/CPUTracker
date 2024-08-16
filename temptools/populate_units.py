import sqlite3

# Connect to the database
conn = sqlite3.connect('cputracker.db')
cursor = conn.cursor()

# Insert example records into the UNITS table
units_data = [
    ('9KQ5064X20158', '100-000000346', '20231020', 'US', '9KQ5064X20158_100-000000346'),
    ('9KC4399M10022', '100-000000334', '20231021', 'CN', '9KC4399M10022_100-000000334'),
    ('9KQ5064X20159', '100-000000347', '20231022', 'US', '9KQ5064X20159_100-000000347'),
    ('9KC4399M10023', '100-000000335', '20231023', 'CN', '9KC4399M10023_100-000000335'),
    ('9KQ5064X20160', '100-000000348', '20231024', 'US', '9KQ5064X20160_100-000000348')
]

for serial_number, part_number, datecode, country, composite_snpn in units_data:
    cursor.execute('''
        INSERT INTO UNITS (serial_number, part_number, datecode, country, composite_snpn)
        VALUES (?, ?, ?, ?, ?)
    ''', (serial_number, part_number, datecode, country, composite_snpn))

# Commit the changes
conn.commit()

# Close the connection
conn.close()
