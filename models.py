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
	username = db.Column(db.String, nullable=False)
	password = db.Column(db.String, nullable=False)

class Rating(db.Model):
	__tablename__ = "local_ratings"
	id = db.Column(db.String, primary_key=True)
	isbn = db.Column(db.String, db.ForeignKey("books.isbn"), nullable=False)
	user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
	review = db.Column(db.String, nullable=False)
	score = db.Column(db.Integer, nullable=False)
	book = db.relationship(Book, back_ref='users')
