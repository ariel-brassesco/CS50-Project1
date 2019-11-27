import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
#engine = create_engine(os.getenv("DATABASE_URL"))
#db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/user", methods=["POST"])
def user():
    name=request.form.get("name")
    username=request.form.get("username")
    password=request.form.get("password")

    return render_template("user.html",username=username, password=password, name=name)

@app.route("/registration", methods=["GET"])
def registration():
    return render_template("registration.html")

