from werkzeug.exceptions import abort
from flasker.auth import login_required
from flasker.db import get_db
from flasker import logger
from pathlib import Path
from werkzeug.security import check_password_hash, generate_password_hash
import os
from werkzeug.utils import secure_filename
from flask import render_template, request, url_for, redirect, Blueprint, flash, g, send_from_directory, session

from flask import Blueprint, render_template

bp = Blueprint('blog', __name__)

UPLOAD_FOLDER = Path(__file__).parent/"static"/"images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Required functions
def get_post(id, check_author=True):

    post = get_db().execute("""
        SELECT p.id, title, img, body, created, author_id, username
        FROM post p JOIN user u ON p.author_id= u.id
        WHERE p.id = ?""",(id,)).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exists.")

    adminPass = os.getenv("ADMIN_PASSWORD")
    
    if check_password_hash(g.user['password'], adminPass):
        pass
    elif check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# TODO: create an image resizer function using pillow

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute("""
        SELECT p.id, title, img, body, created, author_id, username
        FROM post p JOIN user u ON p.author_id = u.id
        ORDER BY created DESC""").fetchall()
    
    
    return render_template('blog/index.html', posts=posts)

@bp.route("/post/<int:id>")
def blog_post(id: int):

    db = get_db()

    post = db.execute("SELECT * FROM post WHERE id=(?)", (id,)).fetchone()
    user = db.execute("SELECT * FROM user WHERE id=(?)", (post['author_id'], )).fetchone()

    return render_template('blog/blog.html', post=post, user=user)
 
@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        
        title = request.form["title"]
        img = request.files["img"]
        body = request.form["body"]

        error = None
        if not title:
            error = "Title is required."
        if not body:
            error = "Post content required"
        if img.filename and not allowed_file(img.filename):
            error = "Only Images Allowed"
        
        if error is not None:
            flash(error, category="error")
        else:
            # Save the image
            imgName = secure_filename(img.filename)
            imgPath = os.path.join(UPLOAD_FOLDER, imgName)
            img.save(imgPath)

            saveimg = "images/" + imgName

            db = get_db()
            db.execute(
                "INSERT INTO post (title, img, body, author_id) VALUES (?, ?, ?, ?)", (title, saveimg, body, g.user["id"])
            )
            db.commit()
            flash("Post uploaded successfully", category="info")
            return redirect(url_for("blog.index"))
        
    return render_template("blog/create.html")

@bp.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        img = request.files["img"]
        body = request.form["body"]
        
        error = None
        if not title:
            error = "Title is required."
        if not body:
            error = "Post content required"
        if img.filename and not allowed_file(img.filename):
            error = "Only Images Allowed"

        if error is not None:
            flash(error, category="error")
        else:

            # Update image if changed
            if img.filename:

                #remove previous image if not empty
                if post["img"]:
                    os.remove( Path(__file__).parent/"static"/str(post["img"]))

                # Save New image
                imgName = secure_filename(img.filename)
                imgPath = os.path.join(UPLOAD_FOLDER, imgName)
                img.save(imgPath)

                saveimg = "images/" + imgName

                #Update database
                db = get_db()
                db.execute("UPDATE post SET title = ?, img = ?, body = ? WHERE id= ?", (title, saveimg, body, id))

                db.commit()
                flash("Post updateded successfully", category="info")
                return redirect(url_for("blog.index"))


            # Update database
            db = get_db()
            db.execute("UPDATE post SET title = ?, body = ? WHERE id= ?", (title, body, id))

            db.commit()
            flash("Post updateded successfully", category="info")

            if check_password_hash(g.user["password"], os.getenv('ADMIN_PASSWORD')):
                return redirect(url_for("admin.admin_pannel"))

            return redirect(url_for("blog.index"))
    

    return render_template("blog/update.html", post=post)

@bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):

    get_post(id)
    db = get_db()

    db.execute("DELETE FROM POST WHERE id = ?", (id, ))
    db.commit()
    flash("Post deleted successfully", category="info")

    if check_password_hash(g.user["password"], os.getenv('ADMIN_PASSWORD')):
        return redirect(url_for("admin.admin_pannel"))
    
    return redirect(url_for("blog.index"))

@bp.route("/img/<imagepath>")
@login_required
def get_image(imagepath):
    return send_from_directory(UPLOAD_FOLDER, imagepath)