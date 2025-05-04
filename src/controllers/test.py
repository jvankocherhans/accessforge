from flask import Blueprint
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

from flask import render_template, request, redirect, url_for, flash
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer

from ldapmanager import LDAPManager

test_blueprint = Blueprint('test_blueprint', __name__)

@test_blueprint.route("/test", methods=["GET"])
def index():
  return "test.get_users()"
