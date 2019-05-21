from os import environ

from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, render_template
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy

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
from . import models

@app.before_first_request
def init_tables():
    # Create tables defined above if they don't exist otherwise load them in
    db.create_all()


@app.route('/')
def home():
    print(db.metadata.tables)
    return render_template("home.html")

@app.route('/about-us')
def about():
    return render_template("about-us.html")

# Needs to be able to handle the current library system
@app.route('/library')
def library():
    return "Books are for nerds"

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
