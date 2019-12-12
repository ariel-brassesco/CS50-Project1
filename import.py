import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    # Create a table of books, a table for users and a table for reviews
    book_table=('CREATE TABLE IF NOT EXISTS books '
                '(id SERIAL PRIMARY KEY, '
                'isbn VARCHAR NOT NULL, '
                'title VARCHAR NULL, '
                'author VARCHAR NULL, '
                'year INTEGER NULL)')

    users_table=('CREATE TABLE IF NOT EXISTS users '
            '(id SERIAL PRIMARY KEY, '
            'username VARCHAR NOT NULL, '
            'password VARCHAR NOT NULL, '
            'name VARCHAR NOT NULL)')

    reviews_table=('CREATE TABLE IF NOT EXISTS reviews '
            '(id SERIAL PRIMARY KEY, '
            'review VARCHAR NOT NULL, '
            'rating INTEGER DEFAULT 1, '
            'id_book INTEGER REFERENCES books, '
            'id_user INTEGER REFERENCES users)')

    # Load the tables in database
    db.execute(book_table)
    db.execute(users_table)
    db.execute(reviews_table)
    db.commit()  # close the transaction finished

    # Import the csv and load the data in books table in database
    columns=list()
    with open("books.csv") as f:
        reader = csv.reader(f)
        columns=next(reader)

        # Load the data in database
        for isbn, title, author, year in reader: # loop gives each column a name
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                        {"isbn": isbn, "title": title, "author": author, "year": int(year)})
            db.commit()


if __name__ == "__main__":
    main()




  