import sqlite3, psycopg2, click, psycopg2.extras
from  flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if "db" not in g:

        
        database = psycopg2.connect(current_app.config["POSTGRES_DB"])
        """ database = psycopg2.connect(
            database=current_app.config["POSTGRES_DATABASE"],
            user=current_app.config["POSTGRES_USER"],
            password=current_app.config["POSTGRES_PASSWORD"],
            host=current_app.config["POSTGRES_HOST"],
            port=current_app.config["POSTGRES_PORT"],
        ) """
        #g.db = database.cursor()
        g.db = database

        """ g.db = sqlite3.connect(current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row """

    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    
    if db is not None:
        db.close()


def init_db():
    connection = get_db()
    db = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    with current_app.open_resource("schema.sql") as f:
        db.execute(f.read().decode("utf8"))

# click module for quick bash scripts
@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)