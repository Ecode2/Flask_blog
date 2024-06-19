# Thi is the application factory 
# where any configurations for the app occurs
# It makes the app to be apackage

import os, logging
from flask import Flask
from pathlib import Path
from dotenv import load_dotenv

# Initialising logger object
hdlr = logging.StreamHandler()
hdlr.formatter = logging.Formatter("%(filename)s :: %(funcName)s :: %(levelname)s -> %(message)s")

logger = logging.Logger("FLASKER_logger")
logger.addHandler(hdlr)

 
def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    logger.info(f"Server object created")
    load_dotenv(override=True)

    app.config.from_mapping(
            SECRET_KEY=b'\xf9\xbd\'}y"\xdf\xbe\r\xd7\xb4\xcfa[T\xd4',
            DATABASE=os.path.join(app.instance_path, "flasker.sqlite"),
            POSTGRES_DB=os.getenv("POSTGRES_DB"),
            POSTGRES_DATABASE=os.getenv("POSTGRES_DATABASE"),
            POSTGRES_USER=os.getenv("POSTGRES_USER"),
            POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD"),
            POSTGRES_HOST=os.getenv("POSTGRES_HOST"),
            POSTGRES_PORT=os.getenv("POSTGRES_PORT")

    )

    UPLOAD_FOLDER = Path(__file__).parent/"static"/"images"

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # set upload size limit to 16mb
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)

    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    
    # initialise database
    from . import db
    with app.app_context():
        logger.info(f"initializing Database object ...")
        db.init_db()
        db.init_app(app=app)


    logger.info(f"initializing Blueprints ...")
    # register authentication and blog blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    # set the url_prefix to / with the endpoint route function to be index() 
    app.add_url_rule("/", endpoint="index")

    # register admin pannel blueprint
    from . import admin
    app.register_blueprint(admin.bp)


    return app
