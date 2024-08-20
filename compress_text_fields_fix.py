import sqlite3
import zlib

def compress_text(text):
    return zlib.compress(text.encode('utf-8'))

def compress_logs():
    conn = sqlite3.connect('cputracker.db')
    cursor = conn.cursor()
    
    # Retrieve all records from the LOGS table
    cursor.execute("SELECT id, host_status, csv_file_content FROM LOGS")
    logs = cursor.fetchall()
    
    for log in logs:
        log_id = log[0]
        host_status = log[1]
        csv_file_content = log[2]
        
        # Compress the text fields
        compressed_host_status = compress_text(host_status)
        compressed_csv_file_content = compress_text(csv_file_content)
        
        # Update the record with the compressed data
        cursor.execute("""
            UPDATE LOGS
            SET host_status = ?, csv_file_content = ?
            WHERE id = ?
        """, (compressed_host_status, compressed_csv_file_content, log_id))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Run the script
compress_logs()