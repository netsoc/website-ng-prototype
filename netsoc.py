from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template("hello.html", name="Jeff")

@app.route('/about-us')
def about():
    return "There is nothing to tell"

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
    return "Bunch of fools"

@app.route('/services')
def services():
    return "Bunch of fools"

@app.route('/wiki')
def wiki():
    return "unhelpful and outdated info"

@app.route('/new-members')
def new_members():
    return "Blah"

# Not sure how accurate or necessary this page is
@app.route('/file-storage')
def file_storage():
    return "Blah"

# Not sure how accurate or necessary this page is
@app.route('/mailing-lists')
def mail_lists():
    return "Blah"

@app.route("/slides")
def slides():
    return "Read a book"

@app.route("/login")
def login():
    return "Must be a member"


# Can use following code if you don't want to set environment variables
if __name__ == '__main__':
   app.run(debug=True)