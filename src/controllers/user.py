from flask import Blueprint
from controllers.decorater import requires_access_level
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

users_blueprint = Blueprint('users_blueprint', __name__)

@users_blueprint.route("/login", methods=["GET", "POST"])
def login():
    pass


@users_blueprint.route("/dashboard", methods=["GET", "POST"])
@requires_access_level(ACCESS['guest'])
def dashboard():
    pass

@users_blueprint.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    pass