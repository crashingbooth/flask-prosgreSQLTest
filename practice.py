import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
	print("get books from what year?")
	books = db.execute("SELECT * FROM books WHERE year='1981'").fetchall()
	print(books)


if __name__ == "__main__":
	main()


	
