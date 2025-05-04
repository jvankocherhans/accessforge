from flask import Blueprint
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

from flask import render_template, request, redirect, url_for, flash
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer

from controllers.decorator import requires_access_level
from model.ACCESS import ACCESS

def create_search_blueprint(ldapmanager_conn):
  search_blueprint = Blueprint('search_blueprint', __name__)

  @search_blueprint.route("/search", methods=["GET", "POST"])
  @requires_access_level(ACCESS['user'])
  def search():
    
    is_admin = current_user.is_admin()
    
    if request.method in ('POST'):
    
      search_type = request.form.get('search-type')
      search_input = request.form.get('search-input')
      
      print(search_input)
      print(search_type)
      
      match(search_type):
        case "group":
          return render_template('listing_group.html', is_admin=is_admin)
        case "user":
          return render_template('listing_user.html', is_admin=is_admin)
    else:
      return render_template('search.html', is_admin=is_admin)
    
  
  @search_blueprint.route("/search/users", methods=["GET", "POST"])
  @requires_access_level(ACCESS['user'])
  def search_users():
    users = ldapmanager_conn.search_users("thier")  # Get the list of LdapUser objects
    return [item.to_dict() for item in users]
    
    
  return search_blueprint
    
