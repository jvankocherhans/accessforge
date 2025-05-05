from flask import Blueprint, session
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
      if "user_cart" not in session:
          session["user_cart"] = []

      if request.method == "POST":
          if "add_user" in request.form:
              username = request.form["add_user"]
              # Avoid duplicates
              if not any(u["username"] == username for u in session["user_cart"]):
                  session["user_cart"].append({
                      "username": username
                  })
                  session.modified = True

      searchinput = request.form.get("searchinput", "")
      users = ldapmanager_conn.search_users(searchinput)

      return render_template(
          "test/test_list_users.html", 
          users=users, 
          searchinput=searchinput, 
          cart_names=[user["username"] for user in session["user_cart"]], 
          amount_users=len(session["user_cart"])
      )

    

  @search_blueprint.route("/search/groups", methods=["GET", "POST"])
  @requires_access_level(ACCESS['user'])
  def search_groups():
      if "cart" not in session:
          session["cart"] = []

      if request.method == "POST":
          if "add_group" in request.form:
              groupname = request.form["add_group"]
              description = request.form["description"]
              
              # Avoid duplicates
              if not any(g["groupname"] == groupname for g in session["cart"]):
                  session["cart"].append({
                      "groupname": groupname,
                      "description": description
                  })
                  session.modified = True

      searchinput = request.form.get("searchinput", "") 
      groups = ldapmanager_conn.search_groups(searchinput)

      return render_template("test/test_list_groups.html", groups=groups, searchinput=searchinput, cart_names=[group["groupname"] for group in session["cart"]], amount_groups=len(session["cart"]))
      
      
  @search_blueprint.route("/shopping-cart", methods=["GET"])
  @requires_access_level(ACCESS['user'])
  def shopping_cart():
      if "cart" not in session or len(session["cart"]) == 0:
          session["cart"] = []
          return redirect(url_for("search_blueprint.search_groups"))

      users = ldapmanager_conn.get_all_users()  # Ensure this returns LdapUser objects
      return render_template('test/test_shopping_cart.html', groups=session["cart"], users=users)






    
  return search_blueprint

    
    
