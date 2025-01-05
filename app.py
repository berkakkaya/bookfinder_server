from flask import Flask

from routes import register_blueprints

app = Flask(__name__)
register_blueprints(app)


@app.route("/")
def hello_world():
    return "Hello, World!"


if __name__ == "__main__":
    app.run()
