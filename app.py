from flask import Flask, g, render_template, request, redirect, url_for, session
import bcrypt
import joblib
import numpy as np
import os
import sqlite3
from urllib.parse import urlparse, unquote

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_DRIVER_AVAILABLE = True
except ImportError:
    mysql = None
    MySQLError = None
    MYSQL_DRIVER_AVAILABLE = False

app = Flask(__name__)
app.url_map.strict_slashes = False

# =========================
# SECRET KEY
# =========================
app.secret_key = os.environ.get('SECRET_KEY', 'secret123')

# =========================
# DATABASE CONFIGURATION
# =========================
DATABASE_URL = os.environ.get('DATABASE_URL')
MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306)) if os.environ.get('MYSQL_PORT') else 3306
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DB = os.environ.get('MYSQL_DB')
SQLITE_PATH = os.environ.get(
    'DATABASE',
    os.path.join(os.path.dirname(__file__), 'thyroid_app.db')
)

if DATABASE_URL:
    parsed_url = urlparse(DATABASE_URL)
    if parsed_url.scheme.startswith('mysql'):
        MYSQL_HOST = MYSQL_HOST or parsed_url.hostname
        MYSQL_PORT = parsed_url.port or MYSQL_PORT
        MYSQL_USER = MYSQL_USER or unquote(parsed_url.username or '')
        MYSQL_PASSWORD = MYSQL_PASSWORD or unquote(parsed_url.password or '')
        MYSQL_DB = MYSQL_DB or parsed_url.path.lstrip('/')
    elif parsed_url.scheme.startswith('sqlite'):
        SQLITE_PATH = parsed_url.path or SQLITE_PATH

USE_MYSQL = bool(
    MYSQL_HOST
    and MYSQL_USER
    and MYSQL_PASSWORD
    and MYSQL_DB
    and MYSQL_DRIVER_AVAILABLE
)


def adapt_query(query):
    return query.replace('?', '%s') if USE_MYSQL else query


def get_db():
    if 'db' not in g:
        if USE_MYSQL:
            g.db = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                auth_plugin='mysql_native_password'
            )
        else:
            g.db = sqlite3.connect(SQLITE_PATH)
            g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def execute_db(query, params=(), fetch_one=False, commit=False):
    db = get_db()
    sql = adapt_query(query)

    if USE_MYSQL:
        cursor = db.cursor(dictionary=True)
    else:
        cursor = db.cursor()

    cursor.execute(sql, params)
    result = None

    if commit:
        db.commit()

    if fetch_one:
        result = cursor.fetchone()
    elif not commit:
        result = cursor.fetchall()

    cursor.close()
    return result


def init_db():
    if USE_MYSQL:
        user_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role ENUM('doctor', 'patient') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        prediction_table_sql = """
        CREATE TABLE IF NOT EXISTS predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            age FLOAT NOT NULL,
            tsh FLOAT NOT NULL,
            t3 FLOAT NOT NULL,
            t4 FLOAT NOT NULL,
            result VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    else:
        user_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('doctor', 'patient')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        prediction_table_sql = """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            age REAL NOT NULL,
            tsh REAL NOT NULL,
            t3 REAL NOT NULL,
            t4 REAL NOT NULL,
            result TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """

    execute_db(user_table_sql, commit=True)
    execute_db(prediction_table_sql, commit=True)


def check_db_connection():
    try:
        execute_db('SELECT 1', fetch_one=True)
        backend = 'MySQL' if USE_MYSQL else 'SQLite'
        print(f'Database backend: {backend}')
    except Exception as e:
        print('Database connection failed:', e)
        raise


if MYSQL_HOST and not MYSQL_DRIVER_AVAILABLE:
    raise RuntimeError(
        'MySQL connection is configured, but mysql-connector-python is not installed.'
    )

with app.app_context():
    init_db()
    check_db_connection()

# =========================
# LOAD MODEL
# =========================
model = None

try:

    model_path = os.path.join(
        os.path.dirname(__file__),
        'model.pkl'
    )

    if os.path.exists(model_path):

        model = joblib.load(model_path)

        print("Model Loaded Successfully")

    else:
        print("model.pkl Not Found")

except Exception as e:

    print("Model Error:", e)

# =========================
# HOME PAGE
# =========================
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for('home'))
    return render_template('index.html')

# =========================
# REGISTER
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():

    msg = ""

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', '').strip().lower()

        if not name or not email or not password or role not in ('doctor', 'patient'):
            msg = "Please provide name, email, password, and select a valid role."
        elif '@' not in email:
            msg = "Please enter a valid email address."
        else:
            try:

                hashed_password = bcrypt.hashpw(
                    password.encode('utf-8'),
                    bcrypt.gensalt()
                )

                execute_db(
                    """
                    INSERT INTO users
                    (name, email, password, role)
                    VALUES(?, ?, ?, ?)
                    """,
                    (
                        name,
                        email,
                        hashed_password.decode('utf-8'),
                        role
                    ),
                    commit=True
                )

                msg = "Registration Successful"

            except sqlite3.IntegrityError:
                msg = "Email Already Exists"

            except Exception as e:
                msg = f"Error: {e}"

    return render_template(
        'register.html',
        msg=msg
    )

# =========================
# DOCTOR LOGIN
# =========================
@app.route('/login/doctor', methods=['GET', 'POST'])
def login_doctor():

    msg = ""

    if request.method == 'POST':

        try:

            email = request.form['email']
            password = request.form['password']

            user = execute_db(
                """
                SELECT *
                FROM users
                WHERE email=?
                AND role='doctor'
                """,
                (email,),
                fetch_one=True
            )

            if user:
                stored_password = user['password']
                if bcrypt.checkpw(
                    password.encode('utf-8'),
                    stored_password.encode('utf-8')
                ):
                    session['loggedin'] = True
                    session['id'] = user['id']
                    session['name'] = user['name']
                    session['role'] = user['role']

                    return redirect(
                        url_for('dashboard_doctor')
                    )
                else:
                    msg = "Incorrect Password"
            else:
                msg = "Doctor Account Not Found"

        except Exception as e:

            msg = f"Error: {e}"

    return render_template(
        'login_doctor.html',
        msg=msg
    )

# =========================
# PATIENT LOGIN
# =========================
@app.route('/login/patient', methods=['GET', 'POST'])
def login_patient():

    msg = ""

    if request.method == 'POST':

        try:

            email = request.form['email']
            password = request.form['password']

            user = execute_db(
                """
                SELECT *
                FROM users
                WHERE email=?
                AND role='patient'
                """,
                (email,),
                fetch_one=True
            )

            if user:
                stored_password = user['password']
                if bcrypt.checkpw(
                    password.encode('utf-8'),
                    stored_password.encode('utf-8')
                ):
                    session['loggedin'] = True
                    session['id'] = user['id']
                    session['name'] = user['name']
                    session['role'] = user['role']

                    return redirect(
                        url_for('dashboard_patient')
                    )
                else:
                    msg = "Incorrect Password"
            else:
                msg = "Patient Account Not Found"

        except Exception as e:

            msg = f"Error: {e}"

    return render_template(
        'login_patient.html',
        msg=msg
    )

# =========================
# GENERIC DASHBOARD REDIRECT
# =========================
@app.route('/dashboard')
def dashboard():

    if 'loggedin' not in session:
        return redirect(url_for('home'))

    if session.get('role') == 'doctor':
        return redirect(url_for('dashboard_doctor'))

    if session.get('role') == 'patient':
        return redirect(url_for('dashboard_patient'))

    session.clear()
    return redirect(url_for('home'))

# =========================
# DOCTOR DASHBOARD
# =========================
@app.route('/dashboard/doctor')
def dashboard_doctor():

    if 'loggedin' not in session:
        return redirect(url_for('login_doctor'))

    if session['role'] != 'doctor':
        if session.get('role') == 'patient':
            return redirect(url_for('dashboard_patient'))
        return "Unauthorized Access"

    return render_template(
        'dashboard_doctor.html',
        name=session['name']
    )

# =========================
# PATIENT DASHBOARD
# =========================
@app.route('/dashboard/patient')
def dashboard_patient():

    if 'loggedin' not in session:
        return redirect(url_for('login_patient'))

    if session['role'] != 'patient':
        if session.get('role') == 'doctor':
            return redirect(url_for('dashboard_doctor'))
        return "Unauthorized Access"

    return render_template(
        'dashboard_patient.html',
        name=session['name']
    )

# =========================
# PREDICT
# =========================
@app.route('/predict', methods=['GET', 'POST'])
def predict():

    print("SESSION DATA:", dict(session))

    if 'loggedin' not in session:
        return redirect(url_for('login_patient'))

    if session.get('role') not in ('patient', 'doctor'):
        return redirect(url_for('login_patient'))

    result = ""

    if request.method == 'POST':

        if model is None:
            result = "Prediction Error: model is not available. Please contact the administrator."
        else:
            try:

                age = float(request.form['age'])
                tsh = float(request.form['tsh'])
                t3 = float(request.form['t3'])
                t4 = float(request.form['t4'])

                input_data = np.array([
                    [age, tsh, t3, t4]
                ])

                prediction = model.predict(input_data)[0]

                if prediction == 1:
                    result = "Malignant (Cancer Detected)"
                else:
                    result = "Benign (No Cancer Detected)"

                execute_db(
                    """
                    INSERT INTO predictions
                    (user_id, age, tsh, t3, t4, result)
                    VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session['id'],
                        age,
                        tsh,
                        t3,
                        t4,
                        result
                    ),
                    commit=True
                )

            except Exception as e:
                result = f"Prediction Error: {e}"

    return render_template(
        'predict.html',
        result=result
    )

# =========================
# HISTORY
# =========================
@app.route('/history')
def history():

    if 'loggedin' not in session:
        return redirect(url_for('login_patient'))

    if session.get('role') not in ('patient', 'doctor'):
        return "Unauthorized Access"

    if session.get('role') == 'doctor':
        rows = execute_db(
            """
            SELECT p.*, u.name AS patient_name
            FROM predictions p
            JOIN users u ON u.id = p.user_id
            ORDER BY timestamp DESC
            """
        )
    else:
        rows = execute_db(
            """
            SELECT *
            FROM predictions
            WHERE user_id=?
            ORDER BY timestamp DESC
            """,
            (session['id'],)
        )

    return render_template(
        'history.html',
        predictions=rows
    )

# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('home'))

# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)
