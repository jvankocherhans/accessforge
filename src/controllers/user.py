from flask import Blueprint, jsonify
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

from flask import render_template, request, redirect, url_for, flash, session
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer

from controllers.decorator import requires_access_level, login_access
from model.ACCESS import ACCESS

def create_user_blueprint(ldapmanager_conn):

    user_blueprint = Blueprint('user_blueprint', __name__)

    @user_blueprint.route("/login", methods=["GET", "POST"])
    @login_access()
    def login():
        
        form = LoginValidation()

        if request.method in ('POST') :
            ldap_login_user = form.user_name.data
            ldap_login_password = form.user_password.data

            ldap_user = ldapmanager_conn.authentication(ldap_login_user, ldap_login_password)

            # validate the connection
            if ldap_user:
                login_user(ldap_user)
                session['access'] = ldap_user.access
                success_message = f"Authentication Success "
                return redirect('/search')

            else:
                error_message = f"Authentication Failed"
                return render_template("error.html", error_message=str(error_message))

        return render_template('login.html', form=form)
    
    @user_blueprint.route("/profile", methods=["GET"])
    @requires_access_level(ACCESS['user'])
    def profile():
        return render_template('profile.html', current_user=ldapmanager_conn.get_user(current_user.id))

    @user_blueprint.route("/logout", methods=["GET"])
    @requires_access_level(ACCESS['user'])
    def logout():    
        logout_user()
        session.clear() 
        return redirect("/login")
    
    @user_blueprint.route("/users", methods=["GET"])
    @requires_access_level(ACCESS['admin'])  # Or another access level, depending on your needs
    def get_users():
        # Fetch users from LDAP or database
        users = ldapmanager_conn.get_all_users() 
        return jsonify([{
            'username': user.username,
            'label': f"{user.firstname} {user.lastname} ({user.username})"
        } for user in users])

    return user_blueprint
