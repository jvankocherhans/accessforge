from flask import render_template, request, redirect, url_for, flash
from authentication import *
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer
from helper import get_env_variable

from controllers.user import users_blueprint
from controllers.search import search_blueprint
from controllers.test import test_blueprint

from flask import Flask
from helper import get_env_variable

from ldapmanager import LDAPManager

app = Flask(__name__)


ldapmanager_connection = LDAPManager()

app.config['WTF_CSRF_ENABLED'] = False
app.secret_key = "my_secret_key"

# register blueprints here...
app.register_blueprint(users_blueprint)
app.register_blueprint(search_blueprint)
app.register_blueprint(test_blueprint)

if __name__ == '__main__':
    ldapmanager_connection.get_users()
    app.run(host='0.0.0.0', port=5000, debug=True)
