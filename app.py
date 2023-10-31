from flask import Flask, render_template

# Create a flask instance
app = Flask(__name__)

# Create a route decorator
@app.route("/")
def index():
    
    ''' FILTERS: string methods with | in templates
    safe: renders tags as html and not as text
    capitalize: capitalise the first letter of the text
    lower: puts all text in lowercase
    upper: puts all text in upper case
    title: capitalise every first letter of every word in the txt
    trim: removes extra spaces in the end of the text
    striptags: completely removes any html tags in the text
    '''
    first_name = "Abubakar"
    stuff = "This is Bold Text"
    favourite_pizza = ["pepperoni", "cheese", "mushroom", 41]
    return render_template('index.html', first_name=first_name, stuff=stuff, favourite_pizza=favourite_pizza)


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", username=name)

# custom error page

# Invalid url
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server erroe
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 