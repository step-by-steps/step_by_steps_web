import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request, redirect, url_for, session,send_file,jsonify
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
import io
import os
import matplotlib.font_manager as fm
from matplotlib import rc
import statistics
from dotenv import load_dotenv
import pymysql

load_dotenv()

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
    connection = get_db_connection(db_sensor_data5_config)
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT event_type, location,timestamp FROM sensor_events WHERE event_type = 'pressed'"
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return data

def get_all_sensor_data():
    connection = get_db_connection(db_sensor_data5_config)
    cursor = connection.cursor(dictionary=True)
    
    # 모든 데이터를 최신순으로 가져오기
    query = "SELECT location, event_type, timestamp FROM sensor_events WHERE event_type = 'Pressed' ORDER BY timestamp DESC"
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return data

def get_sensor_data(location):
    conn = pymysql.connect(
        host='221.155.118.13',
        user='ondy',
        password='030104',
        db='sensor_data5',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            # location에 맞는 데이터를 가져오는 쿼리
            sql = "SELECT * FROM sensor_events WHERE location=%s"
            cursor.execute(sql, (location,))
            result = cursor.fetchall()
    finally:
        conn.close()

    return result

@app.route('/all_data')
def all_data():
    data = get_sensor_data5()
    
    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "No data found"}), 404

def get_sensor_press_interval():
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

    location = request.args.get('location', '부엌')  # 기본값은 '부엌'
    sensor_data = get_sensor_data(location)  # location에 맞는 데이터 가져오기
    df = pd.DataFrame(sensor_data)

    # 날짜를 인덱스로 설정하고, 일별 빈도를 계산
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    daily_data = df.resample('D').size()

    if daily_data.empty:
        analysis_text = "해당 위치에 대한 데이터가 없습니다."
        return render_template('step3.html', analysis_text=analysis_text, location_text=location, selected_location=location)

    # 최신 두 날짜의 데이터 비교
    if len(daily_data) > 1:
        latest_value = daily_data.iloc[-1]
        previous_value = daily_data.iloc[-2]

        
        difference = latest_value - previous_value
        if difference > 0:
            analysis_text = f"어제보다 {difference}만큼 늘었습니다."
        elif difference < 0:
            analysis_text = f"어제보다 {-difference}만큼 줄었습니다."
        else:
            analysis_text = "어제와 변동이 없습니다."
    

    location_text = {"부엌": "부엌", "현관": "현관", "화장실": "화장실"}.get(location, "부엌")
    return render_template('step3.html', analysis_text=analysis_text, location_text=location_text, selected_location=location)


@app.route('/plot.png')
def plot_png():
    location = request.args.get('location', '부엌')
    # 데이터를 Pandas DataFrame으로 변환

    sensor_data = get_sensor_data(location)  # location에 맞는 데이터 가져오기
    df = pd.DataFrame(sensor_data)

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
    ax.set_title(f'{location} 사용 빈도수')  # 그래프 제목
    
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
