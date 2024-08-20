import re
from datetime import datetime
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
#  cursor.execute('ALTER TABLE LOGS ADD TO AUDIT;')
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
# cursor.execute("SELECT id, date_added, serial_number, part_number, datecode, country, test_result, composite_snpn,raw_failure FROM UNITS")
# # WHERE serial_number LIKE '9K4367V2008%'") 
# rows = cursor.fetchall()
# for row in rows:
#     print(row)



# cursor.execute('PRAGMA table_info(users);')
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# # Add the 'enabled' column to the 'users' table
# cursor.execute('ALTER TABLE users ADD COLUMN enabled BOOLEAN DEFAULT 0')

# # Commit the changes and close the connection
# conn.commit()

# # Get the CREATE statement for the 'users' table
# cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
# create_statement = cursor.fetchone()

# if create_statement:
#     print(create_statement[0])
# else:
#     print("Table 'users' does not exist.")
# conn.commit()

# # Add the 'enabled' column to the 'UNITS' table
# cursor.execute('ALTER TABLE UNITS ADD COLUMN user_id INTEGER')

# # Add the 'user_id' column to the 'AUDIT' table
# cursor.execute('ALTER TABLE AUDIT ADD COLUMN user_id INTEGER')

# # Add the 'user_id' column to the 'PARTS' table
# cursor.execute('ALTER TABLE PARTS ADD COLUMN user_id INTEGER')

# cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0')

# cursor.execute('UPDATE users set is_admin=1 where username="ariel";')
# cursor.execute('UPDATE users set enabled=1 where username="ariel";')

# cursor.execute('SELECT * FROM users WHERE  username = "ariel";')
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# sql_script = '''
# INSERT INTO UNITS(serial_number,date_added,composite_snpn,datecode,raw_failure) VALUES("9KQ3862X20240","2023-11-13","9KQ3862X20240_100-000000346","2250PGU"," REPLACED CPUFAILED TO RUN METHOD STARTSHELL UEFI ON PLATFORM ILOMSP");
# INSERT INTO UNITS(serial_number,date_added,composite_snpn,datecode,raw_failure) VALUES("9LO4714X20088","2024-07-29","9LO4714X20088_100-000000346","2246PGU","2414XLRO4J FAII3614250464066452 SPECIAL DEBUG: DEFERRED ECC - CONTACT ORACLE PE FOR NEXT STEPS");
# INSERT INTO UNITS(serial_number,date_added,composite_snpn,datecode,raw_failure) VALUES("9LO4019W20031","2024-07-29","9LO4019W20031_100-000000346","2247PGU","2425XLROHH FAIl3541884549915096 FAULT FAULT.CHASSIS.DOMAIN.BOOT AMD.START-FAILED ON FRU/SYS WITH 100% CERTAINTY + 2 OTHER FAULT(S). SEE THE LOG.");
# INSERT INTO UNITS(serial_number,date_added,composite_snpn,datecode,raw_failure) VALUES("9LS8131W20109","2024-07-29","9LS8131W20109_100-000000346","2247PGU","FAI|2483128604208444 424XLR0D5 PECIAL DEBUG: DEFERRED UECC - CONTACT ORACLE PE FOR NEXT STEPS AILED TO RUN SCIO METRICS");
# INSERT INTO UNITS(serial_number,date_added,composite_snpn,datecode,raw_failure) VALUES("9KP4444V20194","2024-07-29","9KP4444V20194_100-000000346","2244PGU"," FAI3557172427614817 2425XLROMH");
# '''


# # Split the script into individual statements
# statements = sql_script.strip().split(';')

# # Execute each statement
# for statement in statements:
#     if statement.strip():
#         print('\n'+statement.strip())
#         cursor.execute(statement.strip())


# # Function to format date to YYYY-MM-DD
# def format_date(date_str):
#     try:
#         date_obj = datetime.strptime(date_str, '%Y-%m-%d')
#         return date_obj.strftime('%Y-%m-%d')
#     except ValueError:
#         return date_str

# ## Split the script into individual statements
# statements = sql_script.strip().split(';')

# # Execute each statement
# for statement in statements:
#     if statement.strip():
#         # Check if the statement is an INSERT statement
#         if statement.strip().upper().startswith('INSERT INTO UNITS'):
#             # Find the date in the statement and format it
#             date_pattern = re.compile(r'\"(\d{4}-\d{1,2}-\d{1,2})\"')
#             statement = date_pattern.sub(lambda m: f'"{format_date(m.group(1))}"', statement)
        
#         print(statement.strip())
#         print(statement.strip() + ';')
#         # cursor.execute(statement.strip() + ';')

# cursor.execute('DELETE FROM UNITS WHERE  date_added != "2024-08-12";')
# Commit the changes
# cursor.execute('UPDATE UNITS SET country = "China" WHERE serial_number="Y990044U20043";')

# sql_script = '''
# UPDATE UNITS set test_result="NFF" WHERE serial_number="9ACC750X30018";
# UPDATE UNITS set test_result="NFF" WHERE serial_number="9MC6953O40026";
# UPDATE UNITS set test_result="NFF" WHERE serial_number="Y990044U20058";
# '''
# # Split the script into individual statements
# statements = sql_script.strip().split(';')

# # Execute each statement
# for statement in statements:
#     if statement.strip():
#         print('\n'+statement.strip())
#         cursor.execute(statement.strip())

# # Create the LOGS table
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS LOGS (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         file_name VARCHAR(100),
#         serial_number VARCHAR(20) NOT NULL,
#         host_status TEXT,
#         csv_file_name VARCHAR(255),
#         csv_file_content TEXT
#     );
# ''')
# conn.commit()

# cursor.execute('PRAGMA table_info(users);')
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# cursor.execute('SELECT * FROM LOGS;')
# rows = cursor.fetchall()
# for row in rows:
#     print(row)


# cursor.execute('ALTER TABLE LOGS ADD COLUMN date_added DATETIME');

# cursor.execute('PRAGMA table_info(LOGS);')
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# conn.commit()


# # Execute the query
# cursor.execute('''
#     SELECT 
#         name AS table_name,
#         SUM(pgsize) AS size
#     FROM 
#         dbstat
#     GROUP BY 
#         name
#     ORDER BY 
#         size DESC;
# ''')

# # Fetch and print the results
# for row in cursor.fetchall():
#     print(f"Table: {row[0]}, Size: {row[1]} bytes")

sql_script ='''
DELETE FROM LOGS WHERE serial_number='9KQ4574X20182';
DELETE FROM LOGS WHERE serial_number='9ABH752W30024';
DELETE FROM LOGS WHERE serial_number='9KQ5018X20130';
DELETE FROM LOGS WHERE serial_number='9ABH752W30024';
DELETE FROM LOGS WHERE serial_number='9MF6672Q40042';
DELETE FROM LOGS WHERE serial_number='9JT6721U10002';
DELETE FROM LOGS WHERE serial_number='9LN1136S20020';
DELETE FROM LOGS WHERE serial_number='9MC9711P40038';
'''

statements = sql_script.strip().split(';')

# Execute each statement
for statement in statements:
    if statement.strip():
        print('\n'+statement.strip())
        cursor.execute(statement.strip())


conn.close()