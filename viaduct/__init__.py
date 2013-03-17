from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

from viaduct.helpers import register_blueprints

# Set up the application and load the configuration file.
application = Flask(__name__)
application.config.from_object('config')

# Set up the login manager, which is used to store the details related to the
# authentication system.
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'signin'

# Set up the database.
db = SQLAlchemy(application)

# Import the modules.
register_blueprints(application, 'blueprints')

import group
import navigation
#import page
import user
import upload
import pimpy

from viaduct.user.views import load_anonymous_user

login_manager.anonymous_user = load_anonymous_user

