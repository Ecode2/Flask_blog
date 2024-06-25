from flask import flash, Blueprint, render_template, request, url_for, redirect, g, send_from_directory
import psycopg2.extras
from werkzeug.exceptions import abort
from flasker.auth import login_required
from flasker.db import get_db
from pathlib import Path
from werkzeug.security import check_password_hash
import os, markdown
from werkzeug.utils import secure_filename

bp = Blueprint('blog', __name__)

UPLOAD_FOLDER = Path(__file__).parent/"static"/"images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Required functions
def get_post(id, check_author=True):

    connection = get_db()
    db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    db.execute("""
        SELECT p.id, title, img, body, created, author_id, username
        FROM post p JOIN users u ON p.author_id= u.id
        WHERE p.id = %s""",(id,))
    post = db.fetchone()

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
    connection = get_db()
    db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    db.execute("""
        SELECT p.id, title, img, body, created, author_id, username
        FROM post p JOIN users u ON p.author_id = u.id
        ORDER BY created DESC""")
    posts = db.fetchall()
    
    
    return render_template('blog/index.html', posts=posts)

@bp.route("/post/<int:id>")
def blog_post(id: int):

    connection = get_db()
    db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    db.execute("SELECT * FROM post WHERE id=(%s)", (id,))
    post = db.fetchone()

    db.execute("SELECT * FROM users WHERE id=(%s)", (post['author_id'], ))
    user = db.fetchone()

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
            print(imgPath, imgName, "iuskjnvrverviu")
            if imgName:
                img.save(imgPath)

            saveimg = "images/" + imgName

            # convert markdown to html
            html_body = markdown.markdown(body)

            connection = get_db()
            db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

            db.execute(
                "INSERT INTO post (title, img, body, author_id) VALUES (%s, %s, %s, %s)", (title, saveimg, html_body, g.user["id"])
            )
            connection.commit()
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

                # convert markdown to html
                html_body = markdown.markdown(body) 

                #Update database
                connection = get_db()
                db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

                db.execute("UPDATE post SET title = %s, img = %s, body = %s WHERE id= %s", (title, saveimg, html_body, id))

                connection.commit()
                flash("Post updateded successfully", category="info")
                return redirect(url_for("blog.index"))


            # Update database
            connection = get_db()
            db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            db.execute("UPDATE post SET title = %s, body = %s WHERE id= %s", (title, body, id))

            connection.commit()
            flash("Post updateded successfully", category="info")

            if check_password_hash(g.user["password"], os.getenv('ADMIN_PASSWORD')):
                return redirect(url_for("admin.admin_pannel"))

            return redirect(url_for("blog.index"))
    

    return render_template("blog/update.html", post=post)

@bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):

    get_post(id)
    connection = get_db()
    db = connection.cursor()

    db.execute("DELETE FROM POST WHERE id = %s", (id, ))
    connection.commit()
    flash("Post deleted successfully", category="info")

    if check_password_hash(g.user["password"], os.getenv('ADMIN_PASSWORD')):
        return redirect(url_for("admin.admin_pannel"))
    
    return redirect(url_for("blog.index"))

@bp.route("/img/<imagepath>")
@login_required
def get_image(imagepath):
    return send_from_directory(UPLOAD_FOLDER, imagepath)