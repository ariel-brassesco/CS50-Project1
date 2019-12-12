import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def check_user(username):
    select = "SELECT COUNT(*) FROM users WHERE username = '{}'".format(username)
    res = db.execute(select).first()
    db.commit()
    return res.count


def validate_password(password):
    import re

    upper=r"[A-Z]"
    numbers=r"[0-9]"
    symbols=r"[\W_]"

    if (' ' in password) or len(password)<8:
        return False

    if not re.search(symbols,password):
        return False
    
    if not re.search(upper,password):
        return False
    
    if not re.search(numbers,password):
        return False

    return True

def check_login(username, password):
    # Get the password of username from database
    select = "SELECT password FROM users WHERE username = '{}'".format(username)
    user = db.execute(select).first()
    db.commit()
     
    # Check password is correct
    if password == user.password:
        return True

    return False

def add_user(username, password, name):

    try:
        # Add the user into database
        db.execute("INSERT INTO users (username, password, name) VALUES (:username, :password, :name)",
                    {"username": username, "password": password, "name": name})
        db.commit()
    
        # Return a dictionary with the user info
        return user_info(username)
        
    except:
        # Return False in case of an error occur
        return False

def user_info(username):
    try:
        # Get the id, username and name of the new user from database
        select = "SELECT id, username, name FROM users WHERE username = '{}'".format(username)   
        user = db.execute(select).first()
        db.commit()
        
        # Return a dictionary with the user info
        data = {'id': user.id, 'username': user.username, 'name': user.name}
        return data

    except:
        # Return False if an error ocurred
        return False

def book_search(isbn = '', title = '', author = ''):
    try:
        select = (f"SELECT * FROM books WHERE isbn LIKE '%{isbn}%' AND title LIKE '%{title}%' AND author LIKE '%{author}%'")

        books = db.execute(select).fetchall()
        db.commit()

        if not books:
            return "There is no result. Please try another search."
    
        return books
    except:
        return "Upps! An error was ocurred."

def book_info(isbn, username):

    info = dict()
    info['review'] = dict()
    info['rev_users'] = list()
    
    # Get information of book and user
    book = book_search(isbn)
    user = user_info(username)
    
    # Put the book information into info dictionary
    for data in book:
        info['id'] = data.id
        info['isbn'] = data.isbn
        info['title'] = data.title
        info['author'] =data.author
        info['year'] = data.year
    
    # Get the Goodreads information and put into info dictionary
    
    gr_info = gr_api_request(info['isbn'])
    
    if gr_info:
        info['gr_avr'] = gr_info['books'][0]['average_rating']
        info['gr_rev'] = gr_info['books'][0]['work_ratings_count']
    else:
        info['gr_avr'] = '-'
        info['gr_rev'] = '-'
    
    # Get reviews from users
    reviews = get_reviews(book_id = info['id'])

    for review in reviews:
        if review.id_user == user['id']:
            info['review'] = {'username': review.username, 'rating': review.rating, 'text': review.review}
        else:
            info['rev_users'].append({'username': review.username, 'rating': review.rating, 'text': review.review})
    
    return info

def new_review(user_id, book_id, rating, review):
    try:
        # To avoid multiple submitions when refresh the page after a submition
        if get_reviews(user_id, book_id):
            return True
        
        db.execute("INSERT INTO reviews (review, rating, id_book, id_user) VALUES (:review, :rating, :id_book, :id_user)",
                    {"review": review, "rating": rating, "id_book": book_id, "id_user": user_id})
        db.commit()
        return True
    except:
        return False

def get_reviews(user_id = None, book_id = None):
    try:
        if user_id == None:
            select = (f"SELECT reviews.*, username FROM reviews JOIN users ON reviews.id_user = users.id WHERE id_book = {book_id} ORDER BY id ASC")
        elif book_id == None:
            select = (f"SELECT reviews.*, username FROM reviews JOIN users ON reviews.id_user = users.id WHERE id_user = {user_id} ORDER BY id ASC")
        else:
            select = (f"SELECT reviews.*, username FROM reviews JOIN users ON reviews.id_user = users.id WHERE id_book = {book_id} AND id_user = {user_id}")

        reviews = db.execute(select).fetchall()
        db.commit()

        return reviews
    except:
        return False

def gr_api_request(isbn):
    import requests
    GR_KEY = "rbNMA0t6AyiZGNBBiKZOw"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GR_KEY, "isbns": isbn})

    if res.status_code == 200:
        return res.json()
   
    return False

def api_info(isbn):
    
    info = dict()
    book = book_search(isbn)
    
    if isinstance(book, str):
        return False

    for data in book:
        info['title'] = data.title
        info['author'] =data.author
        info['year'] = data.year
        info['isbn'] = data.isbn

    # Get the average rating and the number of reviews from our database
    select = f"SELECT COUNT(*), AVG(rating) FROM reviews WHERE id_book IN (SELECT id FROM books WHERE isbn = '{isbn}')"
    try:
        res = db.execute(select).first()
        db.commit()

        # To avoid error with api request
        if not res.count:
            return False
    except:
        return False

    info['review_count'] = res.count
    info['average_score'] = round(float(res.avg),2)

    return info


def main():
    
    # An exaple of the API request
    import requests    
    
    username = 'ariel'
    isbn = '1416949658'
    #res = requests.get("http://127.0.0.1:5000/api/1416949658") # This is not work, is only for users. 
    
    # This is the request way outside the browser
    res = requests.get("http://127.0.0.1:5000/api", params = {'username': username, 'isbn': isbn})
    print(res.text,res.status_code)
    

if __name__ == "__main__":
    main()
