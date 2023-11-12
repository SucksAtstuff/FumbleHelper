from flask import Flask

app = Flask(__name__)

def home():
    return "<h1> Hi </h1>"

if __name__ =="__main__":
    app.run(debug=True)