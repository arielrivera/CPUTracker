import sqlite3

def ensure_date_added_column():
    # Connect to the database
    conn = sqlite3.connect('cputracker.db')
    cursor = conn.cursor()

    # # Check if the column already exists
    # cursor.execute("PRAGMA table_info(LOGS)")
    # columns = [column[1] for column in cursor.fetchall()]

    # if 'date_added' not in columns:
    #     # Add the column without a default value
    #     cursor.execute('ALTER TABLE LOGS ADD COLUMN date_added DATETIME')

    #     # Update existing rows to set the current timestamp
    #     cursor.execute('UPDATE LOGS SET date_added = CURRENT_TIMESTAMP')

    #     # Commit the changes
    #     conn.commit()

    # # Close the connection
    # conn.close()

    # conn = sqlite3.connect('cputracker.db')
    # cursor = conn.cursor()

    # Query the table schema
    cursor.execute('PRAGMA table_info(LOGS)')
    columns = cursor.fetchall()

    # Print the columns
    for column in columns:
        print(column)

    # Close the connection
    conn.close()

# Call the function to ensure the column exists
ensure_date_added_column()