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
    """
    @param ldapmanager_conn: Instance of the LDAP manager used for searching users and groups.
    @param mongo_handler: Instance for logging user activities.

    @return: Configured Flask Blueprint with routes for searching and managing users/groups.

    Creates a Flask Blueprint for search-related functionality, including user and group search, 
    managing a shopping cart for selected users/groups, and displaying relevant results.
    """
    search_blueprint = Blueprint('search_blueprint', __name__)

    @search_blueprint.route("/search", methods=["GET", "POST"])
    @requires_access_level(ACCESS['user'])
    def search():
        """
        Handles the search form submission and redirects to either user or group search based on input.

        @return: Redirects to user or group search page based on the search type.
        """
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
        """
        Handles the user search functionality and adds selected users to the session cart.

        @return: Renders a list of users based on the search input and displays selected users in the cart.
        """
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
        """
        Handles the group search functionality and adds selected groups to the session cart.

        @return: Renders a list of groups based on the search input and displays selected groups in the cart.
        """
        if "cart" not in session:
            session["cart"] = []

        # Get the search input from the query string
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
        """
        Displays the shopping cart for users/groups that have been selected.

        @return: Renders the shopping cart page with the selected groups and a form for assigning users to groups.
        """
        if "cart" not in session or len(session["cart"]) == 0:
            return redirect(url_for("search_blueprint.search_groups"))

        form = AssignUsersForm()
        for group in session["cart"]:
            form.groupnames.append_entry(group["groupname"])

        users = ldapmanager_conn.get_all_users()

        return render_template('shopping_cart.html', form=form, groups=session["cart"], users=users)

    return search_blueprint
