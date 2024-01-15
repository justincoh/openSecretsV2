from flask import Flask

app = Flask(__name__)

# Might be able to do this entirely without a DB
# Just create the files you need and load them up at module import time
# and keep in memory, shouldn't take up too much space this data isn't large
# https://www.pythonanywhere.com/forums/topic/27680/


@app.route("/", methods=["GET"])
def hello_world():
    # Do we want to use jinja?
    return "<p>Hello, World!</p>"


@app.route("/states", methods=["GET"])
def state_summaries():
    return "<p>Hello, World!</p>"


@app.route("/states/<state_code>", methods=["GET"])
def state_by_code(state_code):
    print(f"the state code {state_code}")
    return f"<p>Hello, {state_code}!</p>"


@app.route("/reps", methods=["GET"])
def list_representatives():
    return f"<p>Hello, list_representatives</p>"


@app.route("/reps/<cid>", methods=["GET"])
def get_rep_by_cid(cid):
    return f"<p>candidate id: {cid}</p>"
