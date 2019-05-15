from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
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


# Can use following code if you don't want to set environment variables
if __name__ == '__main__':
   app.run(debug=True)