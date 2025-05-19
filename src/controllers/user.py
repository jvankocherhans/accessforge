from flask import Blueprint, jsonify
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

from flask import render_template, request, redirect, url_for, flash, session
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer

from model.models import UserActivityEnum, FlashMsgType

from controllers.decorator import requires_access_level, login_access
from model.ACCESS import ACCESS

def create_user_blueprint(ldapmanager_conn, mongo_handler):
    """
    @param ldapmanager_conn: Instance of the LDAP manager used for authentication and user retrieval.
    @param mongo_handler: Instance for logging user activities.

    @return: Configured Flask Blueprint with user-related routes.

    Creates a Flask Blueprint for login, logout, profile viewing, and user lookups.
    """

    user_blueprint = Blueprint('user_blueprint', __name__)

    @user_blueprint.route("/login", methods=["GET", "POST"])
    @login_access()
    def login():
        """
        Handles LDAP user login.

        @return: Redirects to /search on success or renders login form with error message.
        """
        form = LoginValidation()

        if request.method in ('POST') :
            ldap_login_user = form.user_name.data
            ldap_login_password = form.user_password.data

            ldap_user = ldapmanager_conn.authentication(ldap_login_user, ldap_login_password)

            # validate the connection
            if ldap_user:
                login_user(ldap_user)
                session['access'] = ldap_user.access
                
                mongo_handler.create_activity(activity_enum=UserActivityEnum.LOGIN, initiator=ldap_user.id)
                                
                return redirect('/search')

            else:
                flash("Authentication Failed", FlashMsgType.ERROR.value)

        return render_template('login.html', form=form)
    
    @user_blueprint.route("/profile", methods=["GET"])
    @requires_access_level(ACCESS['user'])
    def profile():
        """
        Shows the profile of the currently logged-in user.

        @return: Renders the profile page with current user details.
        """
        return render_template('profile.html', current_user=ldapmanager_conn.get_user(current_user.id), origin_endpoint=request.endpoint)
    
    @user_blueprint.route("/user-details", methods=["GET"])
    @requires_access_level(ACCESS['admin'])
    def get_user():
        """
        Returns details of a specific user (admin only).

        @return: Renders profile page of the requested admin.
        """
        user = ldapmanager_conn.get_user(request.args.get("user"))
        return render_template('profile.html', current_user=user, origin_endpoint=request.endpoint)

    @user_blueprint.route("/logout", methods=["GET"])
    @requires_access_level(ACCESS['user'])
    def logout():    
        """
        Logs out the current user and clears the session.

        @return: Redirects to the login page.
        """
        mongo_handler.create_activity(activity_enum=UserActivityEnum.LOGOUT, initiator=current_user.id)
        
        logout_user()
        session.clear() 
            
        return redirect("/login")
    
    @user_blueprint.route("/users", methods=["GET"])
    @requires_access_level(ACCESS['user'])
    def get_users():
        """
        Returns a list of all users for frontend use

        @return: JSON array of user objects (username and label).
        """
        # Fetch users from LDAP or database
        users = ldapmanager_conn.get_all_users() 
        return jsonify([{
            'username': user.username,
            'label': f"{user.firstname} {user.lastname} ({user.username})"
        } for user in users])

    return user_blueprint
