# web_app.py

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, this is your web app!'

if __name__ == '__main__':
    app.run(debug=True)
