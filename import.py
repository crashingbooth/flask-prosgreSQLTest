# import csv
# import os

# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker

# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))

# def main():
# 	f = open("books.csv")
# 	reader = csv.reader(f)
# 	for isbn, title, author, year in reader:
# 		db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
# 			{"isbn": isbn, "title": title, "author": author, "year": year, })
# 		print(f"added {isbn}, {title}, {author}, {year}")
# 	db.commit()

# if __name__ == "__main__":
# 	main()





import csv
import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    f = open("flights.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        book = Book(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print(f"added {isbn}, {title}, {author}, {year}")
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()