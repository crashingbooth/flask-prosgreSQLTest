import os
import hashlib
import uuid

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
db.userSession = None


@app.route("/")
def index():
	
	return render_template("login.html")
	# return render_template("register.html")
    # return "Project 1: TODO"
@app.route("/login")
def login():
 	return render_template("login.html")

@app.route("/register")
def register():
 	return render_template("register.html")

@app.route("/submitRegistration", methods=["POST"])
def submitRegistration():
	username = request.form.get("username")
	password = request.form.get("password")
	passwordRepeat = request.form.get("password-repeat")

	identical_username = db.execute("SELECT username FROM users where username =:username", {"username": username}).fetchall()
	if identical_username:
		return render_template("error.html", message="username already in use")
	if not password == passwordRepeat:
		return render_template("error.html", message="passwords do not match")


	salt = uuid.uuid4().hex
	saltedPassword = salt+password
	saltedPassword =saltedPassword.encode('utf-8')
	hashed = hashlib.sha256(saltedPassword).hexdigest()
	hashed = str(hashed)
	db.execute("INSERT into users (username, password, salt) VALUES (:username, :password, :salt)",
		{"username":username, "password":hashed, "salt":salt})
	db.commit()
	db.userSession = username
	msg = "logged in as " + username + "db.userSession" + db.userSession
	return render_template("success.html", message=msg)

@app.route("/submitLogin", methods=["POST"])
def submitLogin():
	username = request.form.get("username")
	password = request.form.get("password")


	found_user = db.execute("SELECT username, salt, password FROM users where username =:username", {"username": username}).fetchone()
	if not found_user:
		return render_template("error.html", message="no user by that name")

	name = found_user.username
	hashed_password = found_user.password
	salt = found_user.salt
	
	salted_userPassword = (salt+password).encode('utf-8')
	hashed_userPassword = str(hashlib.sha256(salted_userPassword).hexdigest())

	if hashed_userPassword == hashed_password:
		msg = "logged in as " + name
		db.userSession = name
		return render_template("success.html", message=msg)
	else:
		return render_template("error.html", message="invalid username or password")


@app.route("/searchBooks")
def searchBooks():
	if db.userSession == None:
		return render_template("error.html", message="not logged in")
	else:
		return render_template("searchBooks.html")

@app.route("/listBooks")
def listBooks():
	if db.userSession == None:
		return render_template("error.html", message="not logged in")
	else:
		return render_template("listBooks.html")




