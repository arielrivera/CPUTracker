from flask import Flask, g, request, render_template, Response, jsonify, session, redirect, url_for, make_response, flash, stream_with_context
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 , os, shutil, sqlite3, py7zr, sys, zlib, glob
from flask_bootstrap import Bootstrap
from datetime import datetime
import subprocess
import json
from queue import Queue
import tempfile
import threading
from functools import wraps
try:
    from PIL import Image
except ImportError as e:
    raise ImportError("Pillow is not installed. Please install it with: pip install Pillow") from e
import pytesseract
# # Set Tesseract command path from environment variable (default to 'tesseract')
# tesseract_cmd = os.environ.get('TESSERACT_CMD', 'tesseract')
# pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
# try:
#     pytesseract.get_tesseract_version()
# except Exception as e:
#     raise EnvironmentError("Tesseract is not installed or its path is not configured. Please install Tesseract (e.g., 'sudo apt-get install tesseract-ocr') and set TESSERACT_CMD accordingly.") from e
import io
from werkzeug.exceptions import RequestEntityTooLarge

# sys.path.append('./utils')
# from utils.process_logs import start_process, stop_process

# Use environment variable to switch between development and production
from image_processing import can_process_image, extract_text_from_region, separate_sn_pn
DB_PATH = os.getenv('CPUTRACKER_DB_PATH', '/app/database/cputracker.db')

# Add this near the top with other global variables
update_queues = []
last_update_time = datetime.now()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

app = Flask(__name__)

app.secret_key = 'AMD'
# Initialize Bootstrap
bootstrap = Bootstrap(app)

# Increase max upload size to 50 MB to allow processing then reducing files to <=20 MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    return jsonify({'error': 'File too large, maximum allowed size is 50 MB.'}), 413

# Add these new functions before any routes
def notify_clients():
    """Notify all connected clients about a database update"""
    global last_update_time
    last_update_time = datetime.now()
    dead_queues = []
    
    for queue in update_queues:
        try:
            queue.put_nowait(last_update_time.isoformat())
        except:
            dead_queues.append(queue)
    
    # Clean up dead queues
    for queue in dead_queues:
        if queue in update_queues:
            update_queues.remove(queue)

@app.route('/stream')
def stream():
    """SSE endpoint for real-time updates"""
    def event_stream():
        queue = Queue()
        update_queues.append(queue)
        
        try:
            while True:
                # Send initial timestamp
                if len(update_queues) == 1:  # If this is the first connection
                    yield f"data: {last_update_time.isoformat()}\n\n"
                
                # Wait for new updates
                update_time = queue.get()
                yield f"data: {update_time}\n\n"
        except GeneratorExit:
            if queue in update_queues:
                update_queues.remove(queue)
    
    return Response(event_stream(), mimetype='text/event-stream')

def notify_if_units_changed(func):
    """Decorator to notify clients if the UNITS table is modified"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        notify_clients()  # Notify clients after successful database modification
        return result
    return wrapper

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # db = get_db()
    # units = db.execute('SELECT * FROM UNITS').fetchall()
    # db.close()
    # return render_template('index.html', units=units)
    return render_template('index.html')

@app.route('/home')
def home():
    db = get_db()
    units = db.execute('SELECT * FROM UNITS ORDER BY date_added DESC LIMIT 10').fetchall()
    parts = db.execute('SELECT part_number FROM PARTS WHERE enabled = 1').fetchall()
    test_results = db.execute('SELECT DISTINCT test_result FROM UNITS').fetchall()
    db.close()
    return render_template('home.html', parts=parts, test_results=test_results)
# units=units, 

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    
    # Check file size (for logging or future conditional processing)
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    # If very large, we will process and reduce its size below 20MB
    # ...existing code...
    
    try:
        # Open image from file stream
        img = Image.open(file.stream)
    except Exception as e:
        return jsonify({'error': 'Invalid image file'}), 400

    try:
        # Extract text using pytesseract
        extracted_text = pytesseract.image_to_string(img)
    except Exception as err:
        return jsonify({'error': f'Error processing image with pytesseract: {err}. Ensure Tesseract is installed and TESSERACT_CMD is set correctly. See README file for more information.'}), 500

    # Resize image if its width exceeds the max width (e.g., 1024 px)
    max_width = 1024
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.ANTIALIAS)

    # Convert resized image to bytes for saving/storage
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=85)
    img_byte_arr.seek(0)

    # ... Code for saving the image and extracted text as needed ...
    response_data = {
        'sn': 'example_serial',  # Replace with actual data extraction/processing
        'pn': 'example_product',
        'snpn': extracted_text.strip(),
        'raw_failure': 'None'
    }
    
    return jsonify(response_data), 200

@app.route('/get_records', methods=['GET'])
def get_records():
    """Modified to include timestamp"""
    records_per_page = request.args.get('recordsPerPage', '10')
    last_update = request.args.get('last_update')
    
    # If client's last update matches server's, return no content
    if last_update and datetime.fromisoformat(last_update) >= last_update_time:
        return jsonify({'no_change': True})
    
    db = get_db()
    
    if records_per_page == 'all':
        query = 'SELECT id, date_added, serial_number, part_number, datecode, country, test_result, composite_snpn, raw_failure, lkt_datetime FROM UNITS ORDER BY date_added DESC'
        records = db.execute(query).fetchall()
    else:
        records_per_page = int(records_per_page)
        query = 'SELECT id, date_added, serial_number, part_number, datecode, country, test_result, composite_snpn, raw_failure, lkt_datetime FROM UNITS ORDER BY date_added DESC LIMIT ?'
        records = db.execute(query, (records_per_page,)).fetchall()
    
    db.close()
    
    records_list = [dict(record) for record in records]
    return jsonify({
        'records': records_list,
        'timestamp': last_update_time.isoformat()
    })

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/images')
def images():
    return render_template('images.html')














# def decompress_text(compressed_text):
#     return zlib.decompress(compressed_text).decode('utf-8')


@app.route('/get_logs_records', methods=['GET'])
def get_logs_records():
    records_per_page = request.args.get('recordsPerPage', '10')
    serial = request.args.get('serial', '')
    query_sn = ""

    if (serial != ''):
        query_sn += " WHERE serial_number = ?"
        params = [serial]
    else:
        query_sn = ""
        params = []

    db = get_db()
    
    if records_per_page == 'all':
        query = f'SELECT id, file_name, serial_number, host_status, csv_file_name, csv_file_content FROM LOGS {query_sn} ORDER BY id ASC'
        records = db.execute(query, params).fetchall()
    else:
        records_per_page = int(records_per_page)
        query = f'SELECT id, file_name, serial_number, host_status, csv_file_name, csv_file_content FROM LOGS {query_sn} ORDER BY id ASC LIMIT ?'
        params.append(records_per_page)
        records = db.execute(query, params).fetchall()
    
    db.close()

    keys = ['id', 'file_name', 'serial_number', 'host_status', 'csv_file_name', 'csv_file_content']

    records_list = []
    for record in records:
        record_dict = dict(zip(keys, record))
        for key, value in record_dict.items():
            if isinstance(value, bytes):
                record_dict[key] = value.decode('utf-8')  # Convert bytes to str
        records_list.append(record_dict)

    return jsonify({'records': records_list})


@app.route('/settings')
def settings():
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Retrieve user data
        cursor.execute("SELECT id, username, enabled, is_admin FROM users")
        users = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert user data to a list of dictionaries
        users_list = []
        for user in users:
            users_list.append({
                'id': user[0],
                'username': user[1],
                'enabled': user[2],
                'is_admin': user[3]
            })

        file_size_bytes = os.path.getsize('cputracker.db')
        file_size_mb = file_size_bytes / (1024 * 1024)
        file_size_str = f"{file_size_mb:.2f} MB"
         # Define context variables
        db_info = {
            'name': 'cputracker.db',
            'size': file_size_str
        }
        
        # Log folder information
        logs_folder = 'logs_folder'
        logs_info = {
            'exists': os.path.exists(logs_folder),
            'size': '0.00 MB',
            'num_files': 0
        }
        if logs_info['exists']:
            # Calculate total size of the log folder
            total_size_bytes = sum(os.path.getsize(f) for f in glob.glob(os.path.join(logs_folder, '**'), recursive=True) if os.path.isfile(f))
            total_size_mb = total_size_bytes / (1024 * 1024)
            logs_info['size'] = f"{total_size_mb:.2f} MB"

            # Count the number of .7z files in the log folder
            logs_info['num_files'] = len(glob.glob(os.path.join(logs_folder, '*.7z')))

        # Render the template with user data and context variables
        return render_template('settings.html', users=users_list, db_info=db_info, logs_info=logs_info)


    except Exception as e:
        # Handle any errors
        return str(e), 500

@app.route('/delete_user', methods=['POST'])
def delete_user():
    try:
        data = request.get_json()
        user_id = data['user_id']

        conn = get_db()
        cursor = conn.cursor()

        # Delete the user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        # Return a JSON response
        return jsonify({'success': True})

    except Exception as e:
        # Handle any errors
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE  username = ? and enabled=1', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            # return redirect(url_for('index'))
            mode = request.cookies.get('mode', 'search')  # Default to 'search' mode if not found
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('mode', mode)
            return resp
        
        error = "Invalid credentials. Please try again."
        return render_template('login.html', error=error)
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        try:
            conn = get_db()
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))
        except sqlite3.Error as e:
            flash(f'Database error: {e}')
            return redirect(url_for('register'))
        except Exception as e:
            flash(f'An unexpected error occurred: {e}')
            return redirect(url_for('register'))

    
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/reports')
def reports():
    db = get_db()
    parts = db.execute('SELECT part_number FROM PARTS WHERE enabled = 1').fetchall()
    return render_template('reports.html', parts=parts)



@app.route('/search', methods=['POST'])
def search():
    search_box = request.form.get('searchBox')
    part_number = request.form.get('partNumber')
    if not search_box:
        return jsonify(error="Serial number is required"), 400

    # Connect to the SQLite database
    conn = get_db()
    cursor = conn.cursor()

    # Construct the SQL query
    if part_number.lower() == 'any':
        query = "SELECT id, date_added, serial_number, part_number, datecode, country, test_result, composite_snpn,raw_failure,lkt_datetime FROM UNITS WHERE serial_number LIKE ?"
        params = (search_box + '%',)
    else:
        query = "SELECT id, date_added, serial_number, part_number, datecode, country, test_result, composite_snpn,raw_failure,lkt_datetime FROM UNITS WHERE serial_number LIKE ? AND part_number = ?"
        params = (search_box + '%', part_number)

    # print(query)
    # print(params)

    # Execute the query and fetch the results
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the results to a list of dictionaries
    results = []
    for row in rows:
        print(row)
        results.append({
            'id': row[0],
            'date_added': row[1],
            'serial_number': row[2],
            'part_number': row[3],
            'datecode': row[4],
            'country': row[5],
            'test_result': row[6],
            'composite_snpn': row[7],
            'raw_failure': row[8],
            'lkt_datetime': row[9]
            
        })

    return jsonify(results=results)

@app.route('/advanced_search', methods=['POST'])
def advanced_search():
    start_date = request.form.get ('start_date')
    end_date = request.form.get('end_date')
    part_number = request.form.get('part_number')
    test_result = request.form.get('test_result')
    datecode = request.form.get('datecode')
    raw_failure = request.form.get('raw_failure')
    # host_status = request.form.get('host_status')
    lkt_datetime = request.form.get('lkt_datetime')   

    query = "SELECT * FROM UNITS WHERE 1=1"
    params = []

    # if date_range and end_date:
    #     start_date, end_date = date_range.split(' to ')
    #     query += " AND date BETWEEN ? AND ?"
    #     params.extend([start_date, end_date])

    if start_date and end_date:
        query += " AND date_added BETWEEN ? AND ?"
        params.extend([start_date, end_date])

    if part_number and part_number != 'any':
        query += " AND part_number = ?"
        params.append(part_number)

    if test_result and test_result != 'any':
        query += " AND test_result = ?"
        params.append(test_result)

    if datecode:
        query += " AND datecode = ?"
        params.append(datecode)

    if raw_failure:
        query += " AND raw_failure LIKE ?"
        params.append(f"%{raw_failure}%")

    # if host_status:
    #     query += " AND host_status LIKE ?"
    #     params.append(f"%{host_status}%")

    if lkt_datetime:
        query += " AND DATE(lkt_datetime) = DATE(?)"
        params.append(lkt_datetime)

    # print(query)
    conn = get_db()
    results = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify(results=[dict(row) for row in results])

@app.route('/add', methods=['POST'])
@notify_if_units_changed
def add():
    search_box = request.form.get('searchBox')
    part_number = request.form.get('partNumber')
    composite_snpn = request.form.get('compositeSNPN')
    test_result = "Unknown"
   
    if not search_box or not part_number:
        return jsonify(success=False, message="Missing data"), 400

    search_box = search_box.upper()
    
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO units (serial_number, part_number, composite_snpn, test_result) VALUES (?, ?, ?, ?)', (search_box, part_number, composite_snpn, test_result))
        conn.commit()
        success = True
    except Exception as e:
        conn.rollback()
        success = False
        message = str(e)
    finally:
        conn.close()

    if success:
        return jsonify(success=True, message=f"{search_box} added successfully")
    else:
        return jsonify(success=False, message=message)

@app.route('/addpart', methods=['POST'])
def add_part():
    data = request.get_json()
    part_number = data.get('part_number')

    if not part_number:
        return jsonify(success=False, message="Part number is required"), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO parts (part_number) VALUES (?)', (part_number,))
        conn.commit()

        # Fetch the updated list of parts
        cursor.execute('SELECT part_number FROM parts')
        parts = cursor.fetchall()
        parts_list = [{'part_number': part['part_number']} for part in parts]

        success = True
    except Exception as e:
        conn.rollback()
        success = False
        message = str(e)
    finally:
        conn.close()

    if success:
        return jsonify(success=True, parts=parts_list)
    else:
        return jsonify(success=False, message=message)


@app.route('/get_datecode_suggestions', methods=['GET'])
def get_datecode_suggestions():
    query = request.args.get('query', '')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT datecode FROM UNITS WHERE datecode LIKE ?', (f'%{query}%',))
    suggestions = [row['datecode'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(suggestions)

@app.route('/update_record', methods=['POST'])
@notify_if_units_changed
def update_record():
    data = request.form
    record_id = data['record_id']
    composite_snpn = data['comp_snpn']
    serial_number = data['serial_number']
    part_number = data['part_number']
    datecode = data['datecode']
    country = data['country']
    test_result = data['test_result']
    raw_failure = data['raw_failure']

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE UNITS
            SET composite_snpn=?, serial_number =?, part_number = ?, datecode = ?, country = ?, test_result = ?, raw_failure = ?
            WHERE id = ?
        ''', (composite_snpn, serial_number, part_number, datecode, country, test_result, raw_failure, record_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify(success=False, error=str(e))


# --------------------------------- AUDIT AREA START 

def write_to_audit(message, audit_type):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO AUDIT (message, audit_type, date_time)
        VALUES (?, ?, ?)
    ''', (message, audit_type, datetime.now()))
    conn.commit()
    conn.close()

@app.route('/read_audit', methods=['GET'])
def read_audit():
    audit_type = request.args.get('audit_type')
    rowcount = request.args.get('rowcount', default=100, type=int)
    conn = get_db()
    cursor = conn.cursor()
    cursor = conn.cursor()
    
    if audit_type:
        cursor.execute('''
            SELECT * FROM AUDIT
            WHERE audit_type = ? AND date(date_time) = date('now')
            ORDER BY date_time DESC
            LIMIT ?
        ''', (audit_type, rowcount))
    else:
        cursor.execute('''
            SELECT * FROM AUDIT
            WHERE date(date_time) = date('now')
            ORDER BY date_time DESC
            LIMIT ?
        ''', (rowcount,))
   
    
    records = cursor.fetchall()
    conn.close()
    return jsonify(records)

# --------------------------------- AUDIT AREA ENDS 



@app.route('/delete_record', methods=['POST'])
@notify_if_units_changed
def delete_record():
    record_id = request.form['id']
    success = delete_record_from_database(record_id)
    
    if success:
        return jsonify(success=True)
    else:
        return jsonify(success=False)

def delete_record_from_database(record_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM UNITS WHERE id = ?", (record_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return False
        
        return True
    except Exception as e:
        print(f"Error deleting record: {e}")
        return False
    finally:
        # Close the connection
        conn.close()



@app.route('/save_users', methods=['POST'])
def save_users():
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Extract form data
        form_data = request.form

        # Log the form data
        print("Form Data:", form_data)

        # Iterate over the form data and update the database
        for key, value in form_data.items():
            if key.startswith('enabled_'):
                user_id = key.split('_')[1]
                enabled = 1 if value == 'on' else 0
                print(f"Updating ENABLED for UserID {user_id} TO {enabled}")
                cursor.execute("UPDATE users SET enabled = ? WHERE id = ?", (enabled, user_id))
            elif key.startswith('is_admin_'):
                user_id = key.split('_')[2]
                is_admin = 1 if value == 'on' else 0
                print(f"Updating is_admin for UserId {user_id} to {is_admin}")
                cursor.execute("UPDATE users SET is_admin = ? WHERE id = ?", (is_admin, user_id))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        # Return a success response
        return jsonify({'message': 'User settings saved successfully.'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'An error occurred while saving user settings.'}), 500

def run_process_logs():
    process = subprocess.Popen(['python3', 'process_logs.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in iter(process.stdout.readline, ''):
        yield line
    for line in iter(process.stderr.readline, ''):
        yield line

@app.route('/stream_process_logs', methods=['POST'])
def stream_process_logs():
    return Response(run_process_logs(), mimetype='text/plain')

@app.route('/truncate-logs', methods=['POST'])
def truncate_logs():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM LOGS')
        conn.commit()
        cursor.execute('VACUUM')
        conn.close()
        return jsonify({'message': 'Logs table truncated and space reclaimed successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

app.jinja_env.add_extension('jinja2.ext.do')

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Create UNITS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UNITS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            serial_number TEXT,
            part_number TEXT,
            datecode TEXT,
            country TEXT,
            test_result TEXT,
            composite_snpn TEXT,
            raw_failure TEXT,
            lkt_datetime TIMESTAMP
        )
    ''')
    
    # Create PARTS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PARTS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_number TEXT UNIQUE,
            enabled INTEGER DEFAULT 1
        )
    ''')
    
    # Create LOGS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LOGS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            serial_number TEXT,
            host_status TEXT,
            csv_file_name TEXT,
            csv_file_content BLOB
        )
    ''')
    
    # Create AUDIT table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AUDIT (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            audit_type TEXT,
            date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create a default admin user if none exists
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        from werkzeug.security import generate_password_hash
        admin_password = generate_password_hash('admin')
        cursor.execute('INSERT INTO users (username, password, enabled, is_admin) VALUES (?, ?, 1, 1)', ('admin', admin_password))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Check if running in development mode
    if os.getenv('FLASK_ENV') == 'development':
        # Allow specifying a custom database path for development
        dev_db_path = os.getenv('DEV_DB_PATH')
        if dev_db_path:
            DB_PATH = dev_db_path
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        # Use production settings
        app.run(debug=False)
