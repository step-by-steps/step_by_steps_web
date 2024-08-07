from flask import Flask,render_template
import mysql.connector

app=Flask(__name__)

db_config

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/step1')
def step1():
    return render_template('step1.html')

@app.route('/step2')
def step2():
    return render_template('step2.html')

@app.route('/step3')
def step3():
    return render_template('step3.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/settings')
def settings():
    return "Settings page"
if __name__ == '__main__':
    app.run(debug=True)