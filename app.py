from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def hello():
    return "<h1>welcome to my wtchlist</h1>"

@app.route('/usr/<name>')
def user(name):
    return "welcome~!%s"%name