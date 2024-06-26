import functools

import psycopg2.extras
from flasker.db import get_db
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


bp = Blueprint('auth', __name__, url_prefix="/auth")


@bp.before_app_request # this runs before any view function (app.route()) is runned
def load_logged_in_user():
        
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    
    # connect to database if user is logged in
    else:
        connection = get_db()
        db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        db.execute("SELECT * FROM users WHERE ID = %s",(user_id,))
        g.user = db.fetchone()


@bp.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # get fomrm information
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # connect to database
        connection = get_db()
        db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # ensure form data is filled
        error = None
        if not username:
            error = "Username is required."
        elif not email:
            error = "Email is required."
        elif not password:
            error = "Password is required"

        # ensure that account dosn't exists
        elif db.execute("SELECT id FROM users WHERE username = %s ",(username,)) and db.fetchone() is not None:
            error = f"User {username} is in use! "
        elif db.execute("SELECT id FROM users WHERE email = %s ",(email,)) and db.fetchone() is not None:
            error = f"Email {email} is in use! "

        # if there is no error add account to the database
        if error is None:
            flash("Account created successfully", category="info")
            db.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, generate_password_hash(password)))
            connection.commit()
            return redirect(url_for("auth.login"))
        
        flash(error, category="danger")
    
    return render_template("auth/register.html")
    
        
@bp.route('/', methods=["GET", "POST"])
@bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        # get fomrm information
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # connect to database
        connection = get_db()
        db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # check user info
        db.execute("SELECT * FROM users WHERE username = %s ", (username,))
        user  = db.fetchone()

        print(user)
        # ensure user info is correct
        error = None
        if user is None:
            error = "Username Invalid."

        elif user["email"] != email:
            error = "Email Invalid."

        elif not check_password_hash(user["password"], password):
            error = "Password is Incorrect"


        # if there is no error login user
        if error is None:
            
            # create user session
            session.clear()
            session["user_id"] = user["id"]
            
            session['user_info'] = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'password': user['password']
                }
            
            flash("login successfull", category="success")

            return redirect(url_for("index"))
        
        flash(error, category="warning")
    
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", category="info")
    return redirect(url_for("index"))


def login_required(view):

    # check if user is logged in. if true continew normally, else return to the login page
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        
        return view(**kwargs)
    return wrapped_view