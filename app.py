from flask import Flask, g, request, render_template, Response, jsonify, session, redirect, url_for, make_response, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask_bootstrap import Bootstrap

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
        query = 'SELECT id, date_added, serial_number, part_number, datecode, country,test_result FROM UNITS ORDER BY date_added DESC'
        records = db.execute(query).fetchall()
    else:
        records_per_page = int(records_per_page)
        query = 'SELECT id, date_added, serial_number, part_number, datecode, country,test_result FROM UNITS ORDER BY date_added DESC LIMIT ?'
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
        return 'Invalid credentials'
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
    conn = sqlite3.connect('cputracker.db')  # Replace 'your_database.db' with your actual database file
    cursor = conn.cursor()

    # Construct the SQL query
    if part_number.lower() == 'any':
        query = "SELECT id, date_added, serial_number, part_number, datecode, country FROM UNITS WHERE serial_number LIKE ?"
        # print(query)
        params = (search_box + '%',)
    else:
        query = "SELECT id, date_added, serial_number, part_number, datecode, country FROM UNITS WHERE serial_number LIKE ? AND part_number = ?"
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
        results.append({
            'id': row[0],
            'date_added': row[1],
            'serial_number': row[2],
            'part_number': row[3],
            'datecode': row[4],
            'country': row[5]
        })

    return jsonify(results=results)



@app.route('/add', methods=['POST'])
def add():
    search_box = request.form.get('searchBox')
    part_number = request.form.get('partNumber')
    # Implement your add logic here
    # For example, add the item to the database
    # Basic verification
    if not search_box or not part_number:
        return jsonify(success=False, message="Missing data"), 400

    # Add the new unit to the database
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO units (serial_number, part_number) VALUES (?, ?)', (search_box, part_number))
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

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE UNITS
            SET serial_number =?, part_number = ?, datecode = ?, country = ?, test_result = ?
            WHERE id = ?
        ''', (serial_number, part_number, datecode, country, test_result, record_id))
        conn.commit()
        conn.close()
        return jsonify(success=True)
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify(success=False, error=str(e))



app.jinja_env.add_extension('jinja2.ext.do')

if __name__ == '__main__':
    app.run(debug=True)
