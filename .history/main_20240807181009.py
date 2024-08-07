from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = '011'

db_config = {
    'user': 'ondy',
    'password': '030104',
    'host': '172.20.10.12',
    'database': 'login_data',
    'collation': 'utf8mb4_general_ci'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

def validate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    # 모든 결과를 명시적으로 읽음
    while cursor.nextset():
        cursor.fetchall()
    cursor.close()
    conn.close()
    return user

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = validate_user(username, password)
        if user:
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            return '로그인 실패'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/step1')
def step1():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Step 1 page"

@app.route('/step2')
def step2():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Step 2 page"

@app.route('/step3')
def step3():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Step 3 page"

@app.route('/settings')
def settings():
    if 'username' in session:
        return render_template('settings.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
