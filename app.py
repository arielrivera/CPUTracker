from flask import Flask, g, request, render_template
import sqlite3
from flask_bootstrap import Bootstrap

app = Flask(__name__)

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
    db = get_db()
    units = db.execute('SELECT * FROM UNITS').fetchall()
    # print(units)  # Debugging line to check fetched data
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

# Add this line to include Bootstrap in your HTML template
app.jinja_env.add_extension('jinja2.ext.do')

if __name__ == '__main__':
    app.run(debug=True)