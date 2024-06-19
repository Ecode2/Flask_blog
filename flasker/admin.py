import psycopg2.extras
from werkzeug.exceptions import abort
from flasker.auth import login_required
from flasker.db import get_db
import datetime
from flasker import logger
from flask import render_template, url_for, redirect, Blueprint, flash, session

from flask import Blueprint, render_template

bp = Blueprint('admin', __name__, url_prefix="/admin")


@bp.route('/')
@login_required
def admin_pannel():

    connection = get_db()
    db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
      current_user = session['user_info']
    except KeyError:
      return redirect(url_for('auth.login'))

    db.execute("SELECT * FROM users WHERE username= %s ", ("Admin",))
    admin  = db.fetchone()

    if current_user['username'] != admin['username'] and current_user['email'] != admin['email'] and admin['password']!= current_user['password']:
       abort(401, f"Not Authorised To Access This Page")

    logger.warning(f"Admin Access granted on {datetime.datetime.utcnow()}")

    db.execute("""
        SELECT p.id, title, img, body, created, author_id, username
        FROM post p JOIN users u ON p.author_id = u.id
        ORDER BY created DESC""")
    posts = db.fetchall()
    
    db.execute("SELECT id, username, email FROM users ORDER BY username ASC")
    users = db.fetchall()

    return render_template("admin/admin.html", admin=admin, posts=posts, users=users)

@bp.route("/<int:id>/<string:username>/delete", methods=["POST"])
@login_required
def delete(id, username):

    connection = get_db()
    db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    db.execute("SELECT * FROM users WHERE username = %s", (username,) )
    user = db.fetchone()

    if not user:
       flash("User Doesn't  Exist")
       return redirect(url_for('admin.admin_pannel'))

    db.execute("DELETE FROM users WHERE id = %d And username = %s", (id, username))
    db.execute("DELETE FROM post WHERE author_id = %d", (id, ))
    #db.commit()

    flash(f"User {username} and their post was deleted", category="success")
    return redirect(url_for("admin.admin_pannel"))