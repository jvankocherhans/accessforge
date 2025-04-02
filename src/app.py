from flask import render_template, request, redirect, url_for, flash
from authentication import *
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer
from helper import get_env_variable

from controllers.user import users_blueprint

from flask import Flask
from helper import get_env_variable
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

app = Flask(__name__)

# ldap server hostname and port
ldsp_server = f"ldap://localhost:389"
# dn
root_dn = "dc=castle,dc=com"
# ldap service user and password
ldap_user_name = 'admin'
ldap_password = 'Adminadmin1'
# user
user = f'cn=admin,dc=castle,dc=com'

server = Server(ldsp_server, get_info=ALL)

connection = Connection(server,
                        user=user,
                        password=ldap_password,
                        auto_bind=True)

app.config['WTF_CSRF_ENABLED'] = False
app.secret_key = "my_secret_key"

# register blueprints here...
app.register_blueprint(users_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
