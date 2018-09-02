import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
	yearInput = 1990
	while yearInput != "":
		db.execute("DROP users")
		# print("get books from what year?")
		# yearInput = input()
		# books = db.execute("SELECT title, author FROM books WHERE year=:yearInput", {"yearInput": yearInput}).fetchall()
		# for book in books:
		# 	print(book.title, "-", book.author)


if __name__ == "__main__":
	main()


	
