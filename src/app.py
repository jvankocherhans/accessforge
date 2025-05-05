from flask import render_template, request, redirect, url_for, flash, session
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer
from helper import get_env_variable
from flask_login import LoginManager
from model.ACCESS import ACCESS

from controllers.user import create_user_blueprint
from controllers.search import create_search_blueprint
from controllers.group import create_group_blueprint
from controllers.action import create_action_blueprint

from flask import Flask
from helper import get_env_variable

from ldapmanager import LDAPManager

from model.models import LdapLoginUser, LdapUser

app = Flask(__name__)

ldap_server = get_env_variable("AF_LDAP_SERVER")
base_dn = get_env_variable("LDAP_BASE_DN")
ldap_conn_user_name = get_env_variable("AF_CONN_USER")
ldap_conn_password = get_env_variable("LDAP_ADMIN_PASSWORD")

ldapmanager_conn = LDAPManager(ldap_server, base_dn, ldap_conn_user_name, ldap_conn_password)

app.config['WTF_CSRF_ENABLED'] = False
app.secret_key = "my_secret_key"

login_manager = LoginManager()
login_manager.login_view = "users_blueprint.index"  # wo redirectet wird, wenn nicht eingeloggt
login_manager.init_app(app)

# create and register blueprints here...
user_blueprint = create_user_blueprint(ldapmanager_conn)
search_blueprint = create_search_blueprint(ldapmanager_conn)
group_blueprint = create_group_blueprint(ldapmanager_conn)
action_blueprint = create_action_blueprint(ldapmanager_conn)

app.register_blueprint(user_blueprint)
app.register_blueprint(search_blueprint)
app.register_blueprint(group_blueprint)
app.register_blueprint(action_blueprint)

@login_manager.user_loader
def load_user(user_id):
    access = session.get('access')
    if access is None:
        return None
    return LdapLoginUser(username=user_id, access=access)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
