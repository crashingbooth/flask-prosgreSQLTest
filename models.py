from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
	__tablename__ = "books"
	isbn = db.Column(db.String, primary_key=True)
	author = db.Column(db.String, nullable=False)
	title = db.Column(db.String, nullable=False)
	year = db.Column(db.String, nullable=False)

class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.String, primary_key=True)
	password = db.Column(db.String, nullable=False)

class Rating(db.Model):
	__tablename__ = "local_ratings"
	id = db.Column(db.String, primary_key=True)
	isbn = db.Column(db.String, db.ForeignKey("books.isnb"), nullable=False)
	user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
	review = db.Column(db.String, nullable=False)
	score = db.Column(db.Integer, nullable=False)
