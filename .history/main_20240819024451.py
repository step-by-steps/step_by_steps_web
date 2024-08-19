from flask import Flask, render_template, request, redirect, url_for, session,send_file
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
import io
import os
import matplotlib.font_manager as fm
from matplotlib import rc
import statistics

app = Flask(__name__)
app.secret_key = '011'

db_login_data_config = {
    'user': 'ondy',
    'password': '030104',
    'host': '221.155.118.13',
    'database': 'login_data',
    'collation': 'utf8mb4_general_ci'
}

db_sensor_data5_config = {
    'user': 'ondy',
    'password': '030104',
    'host': '221.155.118.13',
    'database': 'sensor_data5',
    'collation': 'utf8mb4_general_ci'
}

db_sensor_data1_config={
    'user': 'ondy',
    'password': '030104',
    'host': '221.155.118.13',
    'database': 'sensor_data1',
    'collation': 'utf8mb4_general_ci'
}   

db_sensor_data3_config = {
    'user': 'ondy',
    'password': '030104',
    'host': '221.155.118.13',
    'database': 'sensor_data3',
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

def get_sensor_data5():
    # sensor_data1 데이터베이스에 연결
    connection = get_db_connection(db_sensor_data5_config)
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT event_type, location,timestamp FROM sensor_events WHERE event_type = 'pressed'"
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return data

def get_sensor_data1():
    connection = mysql.connector.connect(**db_sensor_data1_config)
    cursor = connection.cursor(dictionary=True)

    # sensor_data1에서 필요한 데이터 가져오기
    query = "SELECT event_type, timestamp FROM sensor_events"
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data  

def get_sensor_data2():
    connection = get_db_connection(db_sensor_data5_config)
    cursor = connection.cursor(dictionary=True)
    
    # duration 데이터 가져오기
    query = "SELECT location, duration FROM sensor_events WHERE event_type = 'pressed'"
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return data

def get_sensor_data3():
    connection = get_db_connection(db_sensor_data3_config)
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT press_interval, timestamp FROM sensor_press_interval"
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
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')
    
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

def get_sensor_press_interval():
    connection = get_db_connection(db_sensor_data3_config)
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT press_interval, timestamp FROM sensor_press_interval"
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return data

    for entry in press_interval_data:
        if entry['press_interval'] > avg_interval * 2:  # 평균보다 2배 이상 긴 간격
            alerts.append({
                'type': 'interval',
                'timestamp': entry['timestamp'],
                'message': f"사용 간격이 평균보다 2배 이상 길었습니다: {entry['press_interval']}밀리초"
            })

    return alerts

@app.route('/alerts')
def alerts():
    if 'username' not in session:
        return redirect(url_for('login'))

    alerts = analyze_press_intervals()
    return render_template('alerts.html', alerts=alerts)

def analyze_press_intervals():
    press_interval_data = get_sensor_press_interval()
    
    intervals = [entry['press_interval'] for entry in press_interval_data]
    avg_interval = statistics.mean(intervals) if intervals else 0
    alerts = []

@app.route('/step2')
def step2():
    if 'username' not in session:
        return redirect(url_for('login'))
    sensor_data5 = get_sensor_data5()
    return render_template('step2.html',sensor_data5=sensor_data5)

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
    sensor_data1 = get_sensor_data1()
    df = pd.DataFrame(sensor_data1)
    
    # 날짜를 인덱스로 설정하고, 일별 빈도를 계산
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    daily_data = df.resample('D').size()

    # 최신 두 날짜의 데이터 비교
    if len(daily_data) > 1:
        latest_date = daily_data.index[-1]
        previous_date = daily_data.index[-2]
        latest_value = daily_data[-1]
        previous_value = daily_data[-2]
        
        difference = latest_value - previous_value
        if difference > 0:
            analysis_text = f"어제보다 {difference}만큼 늘었습니다."
        elif difference < 0:
            analysis_text = f"어제보다 {-difference}만큼 줄었습니다."
        else:
            analysis_text = "어제와 변동이 없습니다."
    else:
        analysis_text = "데이터가 충분하지 않습니다."
    return render_template('step3.html', analysis_text=analysis_text)


@app.route('/plot.png')
def plot_png():
    # 데이터를 Pandas DataFrame으로 변환
    sensor_data1 = get_sensor_data1()
    df = pd.DataFrame(sensor_data1)
    
    # 날짜를 인덱스로 설정하고, 일별로 빈도를 계산
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    daily_data = df.resample('D').size()
    
    # Windows에서 Malgun Gothic 폰트 설정
    font_path = 'C:/Windows/Fonts/malgun.ttf'  # 폰트 경로 (Windows의 경우)
    font_prop = fm.FontProperties(fname=font_path)
    rc('font', family=font_prop.get_name())
    
    # 그래프 생성
    fig, ax = plt.subplots()
    
    # 막대 그래프 생성 및 날짜 형식 지정
    daily_data.plot(kind='bar', ax=ax, color='blue')
    ax.set_xlabel('날짜')  # x축 레이블
    ax.set_ylabel('빈도수')  # y축 레이블
    ax.set_title('화장실 사용 빈도수')  # 그래프 제목
    
    # x축 레이블을 데이터셋에 있는 날짜로 설정
    ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in daily_data.index])
    plt.xticks(rotation=45, ha='right')  # x축 레이블 회전 및 정렬
    
    # 그래프를 이미지로 변환
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return send_file(img, mimetype='image/png')



@app.route('/settings')
def settings():
    if 'username' in session:
        return render_template('settings.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
