from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
import io
import os

app = Flask(__name__)
app.secret_key = '011'

db_login_data_config = {
    'user': 'ondy',
    'password': '030104',
    'host': '221.155.118.13',
    'database': 'login_data',
    'collation': 'utf8mb4_general_ci'
}

db_sensor_data1_config = {
    'user': 'ondy',
    'password': '030104',
    'host': '221.155.118.13',
    'database': 'sensor_data1',
    'collation': 'utf8mb4_general_ci'
}

#공통 DB 연결 함수
def get_db_connection(config):
    connection = mysql.connector.connect(**config)
    return connection

#login_data
def get_login_data():
    connection = get_db_connection(db_login_data_config)
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM some_table_in_login_data"
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return data

def get_sensor_data1():
    # sensor_data1 데이터베이스에 연결
    connection = get_db_connection(db_sensor_data1_config)
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT event_type, location,timestamp FROM sensor_events WHERE event_type = 'pressed'"
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return data

def validate_user(username, password):
    """유저 정보 확인 함수"""
    conn = get_db_connection(db_login_data_config)
    cursor = conn.cursor(dictionary=True, buffered=True)  # buffered=True 추가
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    
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
    sensor_data1 = get_sensor_data1()
    return render_template('step2.html',sensor_data1=sensor_data1)

@app.route('/step2_image')
def step2_image():
    sensor_data = fetch_sensor_data()
    df = pd.DataFrame(sensor_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp').resample('W').size().plot(kind='bar', color='blue')
    plt.title('Sensor Events Over Time')
    plt.xlabel('Week')
    plt.ylabel('Event Count')
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png')

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
