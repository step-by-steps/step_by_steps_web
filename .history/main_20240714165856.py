from flask import Flask,render_temple

app=Flask(__name__)

@app.route('/')
def home():
    return 'this is home!'

if __name__=='__main__':
    app.run('0.0.0.0',post=5000,debug=True)