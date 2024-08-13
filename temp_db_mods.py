import sqlite3

# Connect to the database
conn = sqlite3.connect('cputracker.db')
cursor = conn.cursor()

# cursor.execute('''CREATE TABLE IF NOT EXISTS AUDITNEW (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         serial_number VARCHAR(20),
#         date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
#         message TEXT,
#         audit_type VARCHAR(10) );''')

# # Commit the changes
# conn.commit()

# cursor.execute('DROP TABLE AUDIT;')

# # Commit the changes
# conn.commit()

# cursor.execute('ALTER TABLE AUDITNEW RENAME TO AUDIT;')

# Commit the changes
#conn.commit()
# cursor.execute("INSERT INTO AUDIT (message, audit_type) VALUES ('Tester 2', '7zlogfiles');")

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS UNITSNEW (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
#         date_last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
#         serial_number VARCHAR(20) UNIQUE NOT NULL ,
#         part_number VARCHAR(20),
#         datecode VARCHAR(10),
#         country VARCHAR(15),
#         composite_snpn VARCHAR(30),
#         test_result VARCHAR(10) DEFAULT 'Unknown'
#     );''')
# conn.commit()

# cursor.execute('DROP TABLE UNITS_old;
# cursor.execute('DROP TABLE UNITS_backup;')

# # # # Commit the changes
# conn.commit()

# cursor.execute('ALTER TABLE UNITSNEW RENAME TO UNITS;')


# conn.commit()

# cursor.execute('DELETE FROM UNITS;')

# # # Commit the changes
# conn.commit()

# Step 1: Backup the UNITS table
# cursor.execute("CREATE TABLE UNITS_backup AS SELECT * FROM UNITS")
# conn.commit()
# # # Step 2: Alter the date_added column to DATE
# cursor.execute("ALTER TABLE UNITS RENAME TO UNITS_old")
# conn.commit()

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS UNITS (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         date_added DATE DEFAULT (CURRENT_DATE),
#         serial_number VARCHAR(20) UNIQUE NOT NULL ,
#         part_number VARCHAR(20),
#         datecode VARCHAR(10),
#         country VARCHAR(15),
#         composite_snpn VARCHAR(30),
#         test_result VARCHAR(10) DEFAULT 'Unknown',
#         raw_failure VARCHAR(150)
#     );
# ''')

# # cursor.execute("DROP TABLE UNITS_backup;")

# conn.commit()


# cursor.execute("""
#     INSERT INTO UNITS (date_added,serial_number,part_number,datecode,country,composite_snpn,test_result)
#     SELECT DATE(date_added),serial_number,part_number, datecode,country,composite_snpn,test_result FROM UNITS_backup
# """)
# # cursor.execute("DROP TABLE UNITS_old")

# # Commit the changes and close the connection
cursor.execute("SELECT id, date_added, serial_number, part_number, datecode, country, test_result, composite_snpn,raw_failure FROM UNITS")
# WHERE serial_number LIKE '9K4367V2008%'") 
rows = cursor.fetchall()
for row in rows:
    print(row)




conn.close()