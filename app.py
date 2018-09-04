import os
import hashlib
import uuid
import requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from User import User
from Ratings import Ratings
from keys import keys


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

@app.route("/logout")
def logout():
	db.userSession = None
	return render_template("logout.html")

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
	db.userSession = User(username, salt)
	msg = "logged in as " + username + "db.userSession" + db.userSession
	return render_template("success.html", message=msg, username=db.userSession.username)

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
		db.userSession = User(username, salt)
		return render_template("success.html", message=msg, username=db.userSession.username)
	else:
		return render_template("error.html", message="invalid username or password")


@app.route("/searchBooks")
def searchBooks():
	if db.userSession == None:
		return render_template("error.html", message="not logged in")
	else:
		return render_template("searchBooks.html", username=db.userSession.username)

@app.route("/listBooks", methods=["POST"])
def listBooks(msg = None):
	if db.userSession == None:
		return render_template("error.html", message="not logged in")
	else:
		year = request.form.get("year")
		isbn = request.form.get("isbn")
		if isbn != "":
			books = db.execute("SELECT * from books WHERE isbn=:isbn", {"isbn":isbn})
		else: 
			author = "%" + request.form.get("author") + "%"
			title = "%" + request.form.get("title") + "%"
			year = "%" + request.form.get("year")
			books = db.execute("SELECT * from books WHERE UPPER(author) LIKE UPPER(:author) AND UPPER(title) LIKE UPPER(:title) AND year LIKE :year",
			 {"author": author, "title": title, "year": year})

		return render_template("listBooks.html", books=books, username=db.userSession.username)


# @app.route("/select_book/<string:isbn>")
@app.route("/<isbn>/<year>")
def select_book(isbn, year):
	db.execute("INSERT into favorites (isbn, user_id) VALUES (:isbn, :id)", 
		{ "isbn": isbn, "id": db.userSession.user_id})
	selected = db.execute("SELECT title from books WHERE isbn=:isbn", { "isbn": isbn}).fetchone()
	books = db.execute("SELECT * from books WHERE year=:year", {"year":year})
	db.commit()
	return render_template("listBooks.html", year=year, books=books, msg=selected, username=db.userSession.username)

@app.route("/listFavorites")
def list_favorites():
	favs = db.execute("SELECT DISTINCT b.author, b.title FROM favorites as f LEFT JOIN books as b ON f.isbn = b.isbn WHERE f.user_id=:user_id",
		{"user_id":db.userSession.user_id})
	return render_template("listFavorites.html", username=db.userSession.username, favs=favs)

@app.route("/book/<isbn>")
def book(isbn):
	found_book = db.execute("SELECT * from books WHERE isbn=:isbn",{"isbn": isbn}).fetchone()
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": keys.KEY, "isbns": isbn})
	json = res.json()
	ratings = Ratings()
	books = json["books"]
	if books:
		book = books[0]
		ratings.avgGR = book['average_rating']
		ratings.numGR = book['ratings_count']
	localRatings = db.execute("SELECT count(*) as num, sum(score)/count(*) as avg from local_ratings WHERE isbn =:isbn", {"isbn":isbn}).fetchone()
	ratings.avgLocal = localRatings.num
	ratings.numLocal = localRatings.avg

	userRating = db.execute("SELECT score, review from local_ratings WHERE isbn=:isbn AND user_id=:user_id",{"isbn":isbn, "user_id": db.userSession.user_id } ).fetchone()
	
	if not userRating:
		alreadyRated = False
	else:
		alreadyRated = True

	return render_template("book.html",book=found_book, ratings=ratings, msg=res, alreadyRated=alreadyRated, userRating=userRating)

@app.route("/book/ratings/<isbn>", methods=["POST"])
def submit_rating(isbn):
	userScore = request.form.get("score")
	userReview = request.form.get("review")
	intScore = int(userScore)
	if not intScore:
		return render_template("error.html", message="invalid score")
	db.execute("INSERT INTO local_ratings (user_id, isbn, score, review) VALUES (:user_id, :isbn, :score, :review)",
	 { "user_id": db.userSession.user_id, "isbn":isbn, "score":userScore, "review":userReview })
	db.commit()
	return render_template("add_rating.html")



