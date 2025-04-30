from flask import Blueprint
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

from flask import render_template, request, redirect, url_for, flash
from authentication import *
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer

search_blueprint = Blueprint('search_blueprint', __name__)

@search_blueprint.route("/search", methods=["POST"])
def search():
  
  search_type = request.form.get('search-type')
  search_input = request.form.get('search-input')
  
  print(search_input)
  print(search_type)
  
  match(search_type):
    case "group":
      return render_template('listing/listing_group.html')
    case "user":
      return render_template('listing/listing_user.html')
  
  return render_template('search.html')
  
  
