from flask import Flask,render_template
import mysql.connector

app=Flask(__name__)
app.secret_key = '011'

db_config = {
    'user' : 'cindy',
    'password':'0121aa',
    'host' :'localhost',
    'databace' : 'login_data'
}

