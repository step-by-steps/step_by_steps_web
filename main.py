from flask import Flask,render_template,request,redirect,url_for,session
import mysql.connector

app=Flask(__name__)
app.secret_key = '011'

db_config = {
    'user' : 'cindy',
    'password':'0121aa',
    'host' :'10.50.107.100',
    'database' : 'login_data',
    'collation': 'utf8mb4_general_ci'
}

def validate_user(username, password):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

@app.route('/')
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
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Settings page"

if __name__ == '__main__':
    app.run(debug=True, port=5002)