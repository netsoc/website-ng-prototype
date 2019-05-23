from os import environ

from flask import Flask, abort, render_template
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from werkzeug.middleware.proxy_fix import ProxyFix

import html2text
import tzlocal
from flask_sqlalchemy import SQLAlchemy

timezone = tzlocal.get_localzone()

summarizer = html2text.HTML2Text()
summarizer.ignore_links = True
summarizer.ignore_anchors = True
summarizer.images_to_alt = True
summarizer.ignore_emphasis = True
summarizer.ignore_tables = True


app = Flask(__name__)
# Make sure request.remote_addr represents the real client IP
app.wsgi_app = ProxyFix(app.wsgi_app)


# Configuration is provided through environment variables by Docker Compose
development = not environ['FLASK_ENV'] == 'production'
app.config.update({
    'SECRET_KEY': environ['FLASK_SECRET'],
    # Only want to include port in development mode - in production we will be reverse-proxied
    'SERVER_NAME': f"{environ['PUBLIC_HOST']}:{environ['HTTP_PORT']}" if development else environ['PUBLIC_HOST'],
    # It's CURRENT_YEAR, people
    'PREFERRED_URL_SCHEME': 'http' if development else 'https',
    'SQLALCHEMY_DATABASE_URI': URL(
        drivername='mysql+mysqlconnector',
        username=environ['MYSQL_USER'],
        password=environ['MYSQL_PASSWORD'],
        host='db',
        port=3306,
        database=environ['MYSQL_DATABASE'],
        # Make sure we're using 4-byte UTF-8 for the MySQL connection
        query={'charset': 'utf8mb4'},
    ),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
})

db = SQLAlchemy(app)
from . import library, models
from .library import lookup, books_from_csv
from .models import BlogPost

@app.before_first_request
def init_tables():
    # Create tables defined above if they don't exist otherwise load them in
    db.create_all()

@app.template_filter()
def pretty_authors(post):
    return ', '.join(map(lambda u: u.name, post.authors))
@app.template_filter()
def post_date(time):
    return time.astimezone(timezone).strftime('%Y-%m-%d at %-H:%M')
@app.template_filter()
def html2text(text):
    return summarizer.handle(text)

@app.route('/')
def home():
    posts = BlogPost.query\
            .order_by(BlogPost.time.desc())\
            .paginate(per_page=10)

    return render_template("home.html", posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post = BlogPost.find_one(id)
    if not post:
        return abort(404)

    return render_template("post.html", post=post)

@app.route('/about-us')
def about():
    return render_template("about-us.html")

test = [
        {'title': 'acb','id':1, 'author': 'some person', 'description': 'this is a book about stuff'},
        {'title': 'b','id':2},
        {'title': 'c','id':3},
        {'title': 'd','id':4},
    ]

# Needs to be able to handle the current library system
@app.route('/library/')
@app.route('/library/<search>/<key>')
def library(search=None, key=None):
    #print(search, key)
    books=books_from_csv()
    if search:
        books = [b for b in books if key in b[search]]
    return render_template("library.html", books=books, search=search, key=key)
    # return "Books are for nerds"

@app.route('/library/book/<id>')
def book(id):
    # retrive book from db
    book =lookup(id)
    print(book)
    return render_template('book.html', book=book)

# This one will be a bit awkward as need way to write to openldap
# from snark-www
@app.route('/sign-up')
def sign_up():
    return "Sign up here"

# Basic html page
@app.route('/committee')
def committee():
    return render_template("committee.html")

@app.route('/services')
def services():
    return render_template("services.html")

@app.route('/wiki')
def wiki():
    return render_template("wiki.html")

@app.route('/new-members')
def new_members():
    return render_template("new-members.html")

# Not sure how accurate or necessary this page is
@app.route('/file-storage')
def file_storage():
    return render_template("file-storage.html")

# Not sure how accurate or necessary this page is
@app.route('/mailing-lists')
def mail_lists():
    return "Blah"

@app.route("/slides")
def slides():
    return render_template("slides.html")

@app.route("/login")
def login():
    return "Must be a member"
