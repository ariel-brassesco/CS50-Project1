from flask import Flask, session, render_template, request, redirect, url_for, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from functions import utils as ut


app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Goodreads key
GD_KEY = "rbNMA0t6AyiZGNBBiKZOw"


@app.route("/")
def index():
    return render_template("index.html")

# Render the registration page with corresponding error message
@app.route("/registration", methods = ["GET"])
def registration(error_msg=None):
    return render_template("registration.html",error_msg = error_msg)

# Create a new user if all data is checked.
@app.route("/user", methods = ["POST"])
def new_user():
    # Check if username is already exists
    username = request.form.get("username")

    if ut.check_user(username):
        error_msg = "The username already exists, please try another"
        return registration(error_msg = error_msg)

    # Check if the password is valid
    password = request.form.get("password")
    if not ut.validate_password(password):
        error_msg="The password need to contain more than 8 characters, at least one number, one upper letter and one especial character"
        return registration(error_msg = error_msg)
        
    # Add the new user into database
    name = request.form.get("name")
    session['username'] = ut.add_user(username, password, name)
    
    if not session['username']:
        error_msg="Upps! An error was ocurred. Please Try Again!"
        return registration(error_msg = error_msg)

    return profile(username = session['username']['username'])

# Check that the username and password is correct
@app.route("/user/checking", methods = ["POST"])
def user_check():
    # Get the username and password from the form
    username = request.form.get("username")
    password = request.form.get("password")
    
    if not ut.check_user(username):
        return render_template("index.html", error_msg="The username is not valid.")

    # Check if the password is correct
    if not ut.check_login(username, password):
        return render_template("index.html", error_msg="Invalid password")
    
    # Load the user's data into session
    session['username'] = ut.user_info(username)
    
    if not session['username']:
        error_msg="Upps! An error was ocurred. Please Try Again!"
        return render_template("index.html", error_msg=error_msg)

    return redirect(url_for('profile', username = session['username']['username']))

# Render the profile template
@app.route("/profile/<string:username>")
def profile(username):
    if 'username' not in session:
        return redirect(url_for('index'))

    return render_template("profile.html", username = username)

# Logout function
@app.route("/logout", methods = ['POST', 'GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/book/search", methods=['GET'])
def book_search():
    
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # Search book
    isbn = request.args.get('isbn', None)
    title = request.args.get('title', None)
    author = request.args.get('author', None)
    username = session['username']['username']
    
    # If there is not input in the form ask for input something
    if (isbn == '') and (title == '') and (author == ''):
        return render_template("profile.html", username = username, message = "Please entry at least one field.")
    
    books_find = ut.book_search(isbn, title, author)

    # If there was an error or no match
    if isinstance(books_find, str):
        return render_template("profile.html", username = username, message = books_find)
    
    return render_template("profile.html", username = username, books_find = books_find)

@app.route("/book/<isbn>", methods = ['POST', 'GET'])
def book_page(isbn):
    
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')
        username = session['username']['username']
        user_id = session['username']['id']
        book_info = ut.book_info(isbn, username)
        book_id = book_info['id']
        
        if ut.new_review(user_id, book_id, rating, review):   
            book_info = ut.book_info(isbn, username)    
        else:
            book_info['error_msg']= "An error was ocurred. Please try again."
        
        return render_template('book_page.html', username = username, book = book_info)

    else:
        username = session['username']['username']
        book_info = ut.book_info(isbn, username)
        
        return render_template('book_page.html', username = username, book = book_info)


@app.route("/api/<isbn>")
def book_api(isbn):
    
    if 'username' not in session:
        message = "The API is only available for users. Please login or create an account."
        return jsonify(message), 404

    res = ut.api_info(isbn)
        
    if not res:
        message = "The ISBN doesn't match"
        return jsonify(message), 404
    else:
        return jsonify(res), 200


@app.route("/api")
def api():
    
    isbn = request.args.get('isbn')
    username = request.args.get('username')

    if not ut.check_user(username):
        message = "The username is not valid."
        return jsonify(message), 404

    res = ut.api_info(isbn)
        
    if not res:
        message = "The ISBN doesn't match"
        return jsonify(message), 404
    else:
        return jsonify(res), 200


if __name__ == "__main__":
    app.run(debug=True)
