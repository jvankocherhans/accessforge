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
from forms.AssignUsersForm import AssignUsersForm


def create_search_blueprint(ldapmanager_conn, mongo_handler):
    search_blueprint = Blueprint('search_blueprint', __name__)

    @search_blueprint.route("/search", methods=["GET", "POST"])
    @requires_access_level(ACCESS['user'])
    def search():
        if request.method == "POST":
            search_type = request.form.get('search-type')
            search_input = request.form.get('search-input')

            print(search_input)
            print(search_type)

            if search_type == "group":
                return redirect(url_for('search_blueprint.search_groups', searchinput=search_input))
            elif search_type == "user":
                return redirect(url_for('search_blueprint.search_users', searchinput=search_input))
            
        else:
            return render_template('search.html', is_admin=current_user.is_admin())

    @search_blueprint.route("/search/users", methods=["GET", "POST"])
    @requires_access_level(ACCESS['user'])
    def search_users():
        if "user_cart" not in session:
            session["user_cart"] = []

        searchinput = request.args.get("searchinput")
        
        if request.method == "POST":
            if "add_user" in request.form:
                username = request.form["add_user"]
                # Avoid duplicates
                if not any(u["username"] == username for u in session["user_cart"]):
                    session["user_cart"].append({
                        "username": username
                    })
                    session.modified = True

        # Perform the search with the provided search input
        users = ldapmanager_conn.search_users(searchinput)

        return render_template(
            "listing/listing_user.html",
            users=users,
            searchinput=searchinput,
            cart_names=[user["username"] for user in session["user_cart"]],
            amount_users=len(session["user_cart"]),
            is_admin=current_user.is_admin()
        )

    @search_blueprint.route("/search/groups", methods=["GET", "POST"])
    @requires_access_level(ACCESS['user'])
    def search_groups():
        if "cart" not in session:
            session["cart"] = []

        # Get the search input from the query string (via GET request)
        searchinput = request.args.get("searchinput")
        
        if request.method == "POST":
            if "add_group" in request.form:
                gid = request.form["gid"]
                groupname = request.form["add_group"]
                description = request.form["description"]

                # Avoid duplicates
                if not any(g["groupname"] == groupname for g in session["cart"]):
                    session["cart"].append({
                        "gid": gid,
                        "groupname": groupname,
                        "description": description
                    })
                    session.modified = True

        groups = ldapmanager_conn.search_groups(searchinput)

        return render_template(
            "listing/listing_group.html",
            groups=groups,
            searchinput=searchinput,
            cart_names=[group["groupname"] for group in session["cart"]],
            amount_groups=len(session["cart"]),
            is_admin=current_user.is_admin()
        )

        

    @search_blueprint.route("/shopping-cart", methods=["GET", "POST"])
    @requires_access_level(ACCESS['user'])
    def shopping_cart():
        if "cart" not in session or len(session["cart"]) == 0:
            return redirect(url_for("search_blueprint.search_groups"))

        form = AssignUsersForm()
        for group in session["cart"]:
            form.groupnames.append_entry(group["groupname"])

        users = ldapmanager_conn.get_all_users()

        return render_template('shopping_cart.html', form=form, groups=session["cart"], users=users)

    return search_blueprint
