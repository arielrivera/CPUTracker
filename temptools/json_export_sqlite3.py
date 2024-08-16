import sqlite3
import json

def export_db_to_json(db_path, json_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    db_dict = {}

    for table_name in tables:
        table_name = table_name[0]
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        schema_info = [{'cid': col[0], 'name': col[1], 'type': col[2], 'notnull': col[3], 'dflt_value': col[4], 'pk': col[5]} for col in schema]

        # Get table data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [column[1] for column in schema]
        table_data = [dict(zip(columns, row)) for row in rows]

        db_dict[table_name] = {
            'schema': schema_info,
            'data': table_data
        }

    # Write to JSON file
    with open(json_path, 'w') as json_file:
        json.dump(db_dict, json_file, indent=4)

    # Close the connection
    conn.close()

if __name__ == "__main__":
    db_path = 'cputracker.db'  # Path to your SQLite database
    json_path = 'cputracker_dump.json'  # Path to the output JSON file
    export_db_to_json(db_path, json_path)