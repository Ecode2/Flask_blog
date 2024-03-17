from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash
from flasker.auth import login_required
from flasker.db import get_db
from pathlib import Path
import os, datetime
from flasker import logger
from flask import render_template, request, url_for, redirect, Blueprint, flash, g, session

from flask import Blueprint, render_template

bp = Blueprint('admin', __name__, url_prefix="/admin")


@bp.route('/')
@login_required
def admin_pannel():

    db = get_db()

    try:
      current_user = session['user_info']
    except KeyError:
      return redirect(url_for('auth.login'))

    admin  = db.execute("SELECT * FROM user WHERE username= ? ", ("Admin",)).fetchone()

    if current_user['username'] != admin['username'] and current_user['email'] != admin['email'] and admin['password']!= current_user['password']:
       abort(401, f"Not Authorised To Access This Page")

    logger.warning(f"Admin Access granted on {datetime.datetime.utcnow()}")

    posts = db.execute("""
        SELECT p.id, title, img, body, created, author_id, username
        FROM post p JOIN user u ON p.author_id = u.id
        ORDER BY created DESC""").fetchall()
    
    users = db.execute("SELECT id, username, email FROM user ORDER BY username ASC")



    return render_template("admin/admin.html", admin=admin, posts=posts, users=users)

@bp.route("/<int:id>/<string:username>/delete", methods=["POST"])
@login_required
def delete(id, username):

    db = get_db()
    user = db.execute("SELECT * FROM user WHERE username = ?", (username,) )

    if not user:
       flash("User Doesn't  Exist")
       return redirect(url_for('admin.admin_pannel'))

    db.execute("DELETE FROM user WHERE id = ? And username = ?", (id, username))
    db.execute("DELETE FROM post WHERE author_id = ?", (id, ))
    db.commit()

    flash(f"User {username} and their post was deleted", category="success")
    return redirect(url_for("admin.admin_pannel"))