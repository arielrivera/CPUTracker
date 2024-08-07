from flask import Flask, g, request, render_template, Response
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


@app.route('/logs')
def logs():
    # print("Accessing logs page")  # Debugging statement
    return render_template('logs.html')
    # return Response("This is the logs page.", mimetype='text/plain')


@app.route('/settings')
def settings():
    print("Accessing settings page")  # Debugging statement
    return render_template('settings.html')
    # return Response("This is the settings page.", mimetype='text/plain')


# Add this line to include Bootstrap in your HTML template
app.jinja_env.add_extension('jinja2.ext.do')

if __name__ == '__main__':
    app.run(debug=True)
