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

users_blueprint = Blueprint('users_blueprint', __name__)

@users_blueprint.route("/login", methods=["GET", "POST"])
def index():

    # initiate the form..
    form = LoginValidation()

    if request.method in ('POST') :
        login_user = form.user_name.data
        login_password = form.user_password.data

        login_msg = global_ldap_authentication(login_user, login_password)

        # validate the connection
        if login_msg == "Success":
            success_message = f"*** Authentication Success "
            return render_template('search.html', success_message=success_message)

        else:
            error_message = f"*** Authentication Failed - {login_msg}"
            return render_template("error.html", error_message=str(error_message))

    return render_template('login.html', form=form)

@users_blueprint.route("/profile", methods=["GET"])
def profile():
    return render_template('profile.html')


# @users_blueprint.route("/dashboard", methods=["GET", "POST"])
# @requires_access_level(ACCESS['guest'])
# def dashboard():
#     pass

# @users_blueprint.route("/logout", methods=["GET", "POST"])
# @login_required
# def logout():
#     pass