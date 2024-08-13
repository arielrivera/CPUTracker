from flask import Flask, g, request, render_template, Response, jsonify, session, redirect, url_for, make_response, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 , os, shutil, sqlite3, py7zr
from flask_bootstrap import Bootstrap
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'AMD'
# Initialize Bootstrap
bootstrap = Bootstrap(app)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('cputracker.db')
        db.row_factory = sqlite3.Row  # This allows us to access columns by name
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
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
    db.close()
    return render_template('home.html', units=units, parts=parts)

@app.route('/get_records', methods=['GET'])
def get_records():
    records_per_page = request.args.get('recordsPerPage', '10')
    db = get_db()
    
    if records_per_page == 'all':
        query = 'SELECT id, date_added, serial_number, part_number, datecode, country, test_result, composite_snpn, raw_failure FROM UNITS ORDER BY date_added DESC'
        records = db.execute(query).fetchall()
    else:
        records_per_page = int(records_per_page)
        query = 'SELECT id, date_added, serial_number, part_number, datecode, country, test_result, composite_snpn, raw_failure FROM UNITS ORDER BY date_added DESC LIMIT ?'
        records = db.execute(query, (records_per_page,)).fetchall()
    
    db.close()
    
    # Convert records to a list of dictionaries
    records_list = [dict(record) for record in records]
    
    return jsonify({'records': records_list})

@app.route('/logs')
def logs():
    return render_template('logs.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
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
        query = "SELECT id, date_added, serial_number, part_number, datecode, country, test_result, composite_snpn,raw_failure FROM UNITS WHERE serial_number LIKE ?"
        params = (search_box + '%',)
    else:
        query = "SELECT id, date_added, serial_number, part_number, datecode, country, test_result, composite_snpn,raw_failure FROM UNITS WHERE serial_number LIKE ? AND part_number = ?"
        params = (search_box + '%', part_number)

    print(query)
    print(params)

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
            'raw_failure': row[8]
            
        })

    return jsonify(results=results)



@app.route('/add', methods=['POST'])
def add():
    search_box = request.form.get('searchBox')
    part_number = request.form.get('partNumber')
    composite_snpn = request.form.get('compositeSNPN')
   
    if not search_box or not part_number:
        return jsonify(success=False, message="Missing data"), 400

    search_box = search_box.upper()
    
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO units (serial_number, part_number, composite_snpn) VALUES (?, ?, ?)', (search_box, part_number, composite_snpn))
        conn.commit()
        success = True
    except Exception as e:
        conn.rollback()
        success = False
        message = str(e)
    finally:
        conn.close()

    if success:
        return jsonify(success=True, message="Unit added successfully")
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
def update_record():
    data = request.form
    record_id = data['record_id']
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
            SET serial_number =?, part_number = ?, datecode = ?, country = ?, test_result = ?, raw_failure = ?
            WHERE id = ?
        ''', (serial_number, part_number, datecode, country, test_result, raw_failure, record_id))
        conn.commit()
        conn.close()
        return jsonify(success=True)
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

# --------- LOGS AREA START
# Global variable to ensure the process runs only once
process_running = False

# @app.route('/start_process', methods=['POST'])
# def start_process_route():
#     data = request.get_json()
#     mode = data.get('mode', 'new-files')
#     start_process(mode)
#     return jsonify({"message": "Process started in mode: " + mode})

# @app.route('/stop_process', methods=['POST'])
# def stop_process_route():
#     stop_process()
#     return jsonify({"message": "Process stopped."})

# Moved from abandoned extra py file 
#
def get_serial_number(file_name):
    write_to_audit(f"get_serial_number,  file: {file_name}", '7zlogfiles')
    parts = file_name.split('_')
    if len(parts) > 2:
        return parts[1]
    return None

def process_file(file_path, temp_folder, db):
    write_to_audit(f"process_file,  file_path: {file_path}  temp_folder: {temp_folder}", '7zlogfiles')
    file_name = os.path.basename(file_path)
    serial_number = get_serial_number(file_name)
    if not serial_number:
        write_to_audit("process_file,  Invalid file name format.", '7zlogfiles')
        return "Invalid file name format."

    # Copy file to temp folder
    temp_file_path = os.path.join(temp_folder, file_name)
    shutil.copy(file_path, temp_file_path)
    write_to_audit(f"process_file,  temp_file_path: {temp_file_path}", '7zlogfiles')
    try:
        with py7zr.SevenZipFile(temp_file_path, mode='r') as archive:
            archive.extractall(path=temp_folder)
        write_to_audit("process_file, Extraction of completed successfully.", '7zlogfiles')
        
    except FileNotFoundError:
        write_to_audit(f"Error: File {temp_file_path} not found.", '7zlogfiles')
    except py7zr.exceptions.Bad7zFile:
        write_to_audit(f"Error: {temp_file_path} is not a valid 7z file.", '7zlogfiles')
    except Exception as e:
        write_to_audit(f"An error occurred: {str(e)}", '7zlogfiles')

    # Read Host_Status.txt
    host_status_path = os.path.join(temp_folder, 'Host_Status.txt')
    host_status = None
    if os.path.exists(host_status_path):
        with open(host_status_path, 'r') as file:
            host_status = file.read()

    # Read CSV file
    csv_file_name = None
    csv_file_content = None
    for file in os.listdir(temp_folder):
        if file.startswith(serial_number) and file.endswith('.csv'):
            csv_file_name = file
            with open(os.path.join(temp_folder, file), 'r') as csv_file:
                csv_file_content = csv_file.read()
            break

    # Store data in the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
            INSERT INTO LOGS (file_name, serial_number, host_status, csv_file_name, csv_file_content) 
            VALUES (?, ?, ?, ?, ?)
        """, ('example.7z', '12345', 'active', 'example.csv', 'csv content here'))
    db.commit()

    # Clean up temp folder
    shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    return f"Processed file: {file_name}"

def process_logs(mode):
    global process_running
    write_to_audit('Running function process_logs.', '7zlogfiles')
    if process_running:
        return "Process is already running."
    process_running = True

    logs_folder = "/app/logs_folder"
    temp_folder = "/app/temp_folder"
    db = get_db()

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    files = [os.path.join(logs_folder, f) for f in os.listdir(logs_folder) if f.endswith('.7z')]
    if mode == "new-files":
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    else:
        files.sort(key=lambda x: os.path.getctime(x))

    for file in files:
        result = process_file(file, temp_folder, db)
        write_to_audit(f'process_logs->process_file: {result}.', '7zlogfiles')
        print(result)  # This would be sent to the web interface in a real application

    process_running = False
    return "Process completed."

# def start_process(mode):
#     threading.Thread(target=process_logs, args=(mode,)).start()

# def stop_process():
#     global process_running
#     process_running = False 

# def run_process_logs_in_context():
#     with app.app_context():
#         process_logs()

# ---------
@app.route('/start_process', methods=['POST'])
def start_process_route():
    global process_running
    if not process_running:
        process_running = True
        mode = request.json.get('mode', 'new-files')
        run_process_logs_in_context(mode)
    return jsonify({"message": "Process started in route /start_process"})


@app.route('/stop_process', methods=['POST'])
def stop_process():
    global process_running
    process_running = False
    return jsonify({"message": "Process stopped"})


def run_process_logs_in_context(mode):
    write_to_audit('Within run_process_logs_in_context', '7zlogfiles')
    with app.app_context():
        process_logs(mode)
        
# --------- LOGS AREA END


@app.route('/delete_record', methods=['POST'])
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

app.jinja_env.add_extension('jinja2.ext.do')

if __name__ == '__main__':
    app.run(debug=True)
