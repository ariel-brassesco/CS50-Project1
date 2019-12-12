# Project 1

### Web Programming with Python and JavaScript

## Files Structure
**Libropedia** is a book-search application. The files project organization is explained next:

* `application.py`: Contain the app code.
* Template folder: Contain the `.html` files.
  * `layout.html` - the layout structure for html pages, mainly contain the `<head>` with **Bootstrap 4 library**.
  * `index.html` - the **login** page for users.
  * `registration.html` - the **registration** page for new users.
  * `profile.html` - the **profile** page where users can search books and show the results.
  * `book_page.html` - the **book** page that show the book's information, user's reviews and the form to make a review.
* Static folder: Contain the image folder with the images files used.
* Functions folder: Contain the python modules.
  * `utils.py` - in this module there are functions to manage the database and all tha data user for the app.
* `books.csv`: Contain the books database.
* `import.py`: It's the python module uses for create the tables in database and to import the books data from `books.csv`. This module was run once, and it isn't called by `application.py`.
* `requirements.txt`: Contain the python libraries needed for this project.

## App Characteristics

Libropedia App allows:

* Create an account, Login and Logout.
* Search books by match total or partially ISBN, Title and Author.
* Link the search results to a page with the book information.
* The book page shows Title, Author, Publication year, ISBN, Goodreads rating and number of work reviews. The Goodreads data is getted by the Goodreads's API.
* The user can Logout in the `profile` and `book page`, and come back to search form from book page.
* Also the book page shows the reviews of the users and allows the user to make a review (only one review for user).
* The app has an API for users that response with the book information in JSON format. The users can request the API with route `/api/<isbn>` (**only users**).
* The app's API also allows to request the book information with `requests.get("http://127.0.0.1:5000/api", params = {'username': username, 'isbn': isbn})`.
* All the web pages have Bootstrap 4 and responsive media.

## App Code

* The `html` files are templates with Jinja2.
* The app code avoid unauthorised access to profile, book page or API, and redirect to `index.html`.
* Any request error from database is handled with error message in web page.
* The data forms is handling with `html` options like `required` attribute or by python code.
* The user password has a validation process, and the username is checked for uniqueness with python code.
