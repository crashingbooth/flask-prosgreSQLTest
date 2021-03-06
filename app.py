import os
import hashlib
import uuid
import requests

from flask import Flask, render_template, jsonify, request
from models import *
from keys import keys
from Ratings import AllRatings

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# from flask import Flask, session, render_template, request
# from flask_session import Session
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from keys import keys

# from models import *


# app = Flask(__name__)

# # Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# # Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# # app.config["SESSION_TYPE"] = "filesystem"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db.init_app(app)
# # Session(app)

# # Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))
# db.userSession = None


@app.route("/")
def index():	
	return render_template("login.html")
	# return render_template("register.html")

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

	identical_username = User.query.filter_by(username=username).all()
	if identical_username:
		return render_template("error.html", message="username already in use")
	if not password == passwordRepeat:
		return render_template("error.html", message="passwords do not match")


	id = uuid.uuid4().hex
	saltedPassword = id+password
	saltedPassword =saltedPassword.encode('utf-8')
	hashed = hashlib.sha256(saltedPassword).hexdigest()
	hashed = str(hashed)
	newUser = User(username=username, id=id, password=hashed)
	db.session.add(newUser)
	db.session.commit()
	print(f"name: {newUser.username} id: {newUser.id}, password: {newUser.password}")
	db.userSession = newUser
	msg = "logged in as " + username + "db.userSession" + db.userSession.username
	return render_template("success.html", message=msg, username=username)

@app.route("/submitLogin", methods=["POST"])
def submitLogin():
	username = request.form.get("username")
	password = request.form.get("password")

	found_user = User.query.filter_by(username=username).first()
	if not found_user:
		return render_template("error.html", message="no user by that name")

	name = found_user.username
	hashed_password = found_user.password
	salt = found_user.id
	
	salted_userPassword = (salt+password).encode('utf-8')
	hashed_userPassword = str(hashlib.sha256(salted_userPassword).hexdigest())

	if hashed_userPassword == hashed_password:
		msg = "logged in as " + name
		db.userSession = found_user
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
			books = Book.query.filter_by(isbn=isbn).first()
		else: 
			author = "%" + request.form.get("author") + "%"
			title = "%" + request.form.get("title") + "%"
			year = "%" + request.form.get("year")
			books = Book.query.filter(Book.author.ilike(author)).filter(Book.title.ilike(title)).filter(Book.year.like(year)).all()

		return render_template("listBooks.html", books=books, username=db.userSession.username)

@app.route("/book/<isbn>")
def book(isbn):
	found_book = Book.query.get(isbn)
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": keys.KEY, "isbns": isbn})
	json = res.json()
	ratings = AllRatings()
	books = json["books"]
	if books:
		book = books[0]
		ratings.avgGR = book['average_rating']
		ratings.numGR = book['ratings_count']
	localRatings = Rating.query.filter_by(isbn=isbn).all()
	localCount = len(localRatings)
	localSum = sum([x.score for x in localRatings])
	
	if localCount != 0:
		ratings.avgLocal = localSum / localCount
	ratings.numLocal = localCount

	
	userRating = Rating.query.filter_by(user_id=db.userSession.id).filter_by(isbn=isbn).first()
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
	db.session.add(Rating(id=str(uuid.uuid4().hex), score=userScore, review=userReview, isbn=isbn, user_id=db.userSession.id))
	db.session.commit()
	return render_template("add_rating.html")


@app.route("/reviews")
def list_reviews():
	# j = join(local_ratings, books, local_ratings.isbn==books.isbn)
	# reviews = db.session.query(Book.title, Rating.score, Rating.review).join(Book)filter(Rating.user_id= db.userSession.id).all()
	# for r in reviews:
	# 	print(r.score)

	reviews = db.execute("SELECT b.title, b.author, r.score, r.review from local_ratings as r WHERE r.user_id = :user_id", { "user_id": db.userSession.id}).fetchall()
	# reviews = Rating.query.filter_by(user_id=db.userSession.id).all()
	return render_template("listReviews.html", username=db.userSession.username, reviews=reviews)


