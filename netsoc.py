from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("hello.html", name="Jeff")


# Can use following code if you don't want to set environment variables
if __name__ == '__main__':
   app.run(debug=True)