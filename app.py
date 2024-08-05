from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Database Connection (Replace with your actual database path)
DATABASE = 'cputracker.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    units = db.execute('SELECT * FROM UNITS').fetchall()
    return render_template('index.html', units=units)

@app.route('/add', methods=['POST'])
def add_unit():
    db = get_db()
    serial_number = request.form['serial_number']
    part_number = request.form['part_number']
    # ... (Add other fields)
    db.execute(
        'INSERT INTO UNITS (serial_number, part_number, ...) VALUES (?, ?, ...)',
        (serial_number, part_number, ...)
    )
    db.commit()
    return 'Unit added successfully!'

if __name__ == '__main__':
    app.run(debug=True)
