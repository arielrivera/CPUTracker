import sqlite3
import zlib

def decompress_text(compressed_text):
    if isinstance(compressed_text, str):
        compressed_text = compressed_text.encode('utf-8')
    return zlib.decompress(compressed_text).decode('utf-8')

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
        print(f'\nWorking with logid {log_id}')
        print(f'host_status : {host_status} \n')
        
        try:
            # Decompress the text fields
            decompressed_host_status = decompress_text(host_status)
            decompressed_csv_file_content = decompress_text(csv_file_content)
            
            # Update the record with the decompressed data
            cursor.execute("""
                UPDATE LOGS
                SET host_status = ?, csv_file_content = ?
                WHERE id = ?
            """, (decompressed_host_status, decompressed_csv_file_content, log_id))
            conn.commit()
        except zlib.error as e:
            print(f"Error decompressing log_id {log_id}: {e}")
    
    # Close the connection
    conn.close()

# Run the script
compress_logs()