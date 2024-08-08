from flask import Flask, g, request, render_template, Response, jsonify, session, redirect, url_for
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
    
    db = get_db()
    units = db.execute('SELECT * FROM UNITS').fetchall()
    db.close()
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
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')
    # return '''
    #     <form method="post">
    #         <p><input type=text name=username>
    #         <p><input type=password name=password>
    #         <p><input type=submit value=Login>
    #     </form>
    # '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        conn = get_db()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        # return redirect(url_for('login'))
        return render_template('login.html')
    
    return render_template('register.html')
    # return '''
    #     <form method="post">
    #         <p><input type=text name=username>
    #         <p><input type=password name=password>
    #         <p><input type=submit value=Register>
    #     </form>
    # '''

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Add this line to include Bootstrap in your HTML template
app.jinja_env.add_extension('jinja2.ext.do')

if __name__ == '__main__':
    app.run(debug=True)
