import sqlite3
import csv

# Step 1: Read the list from a CSV file
def read_list_from_csv(file_path):
    items = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            items.append((row[0], row[1]))  # Assuming the CSV has two columns: serial_number, part_number
    return items

# Step 2: Connect to the database
def connect_to_database(db_path):
    conn = sqlite3.connect(db_path)
    return conn

# Step 3: Query the database
def query_database(conn, items):
    results = []
    cursor = conn.cursor()
    for serial_number, part_number in items:
        print(f">{serial_number}<")
        # query = f"SELECT * FROM units WHERE serial_number = '{serial_number}' AND part_number = '{part_number}'"
        # query = "SELECT * FROM units WHERE serial_number AND part_number = ?"
        # print(query)
        # cursor.execute("SELECT * FROM units WHERE serial_number = ? AND part_number = ?", (serial_number, part_number))
        cursor.execute("SELECT * FROM units WHERE serial_number = ?", (serial_number,))
        result = cursor.fetchone()
        if result:
            results.append(result)
    return results

# Step 4: Display the results
def display_results(results):
    for result in results:
        print(result)

# Main function
def main():
    csv_file_path = 'static/sn_list.csv'
    db_path = 'database/cputracker.db'
    
    items = read_list_from_csv(csv_file_path)
    conn = connect_to_database(db_path)
    results = query_database(conn, items)
    display_results(results)
    conn.close()

if __name__ == "__main__":
    main()
