from flask import Flask
from helper import get_env_variable
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

from flask import render_template, request, redirect, url_for, flash
from global_ldap_authentication import *
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer

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


app.config['WTF_CSRF_ENABLED'] = False
app.secret_key = "my_secret_key"


server = Server(ldsp_server, get_info=ALL)

connection = Connection(server,
                        user=user,
                        password=ldap_password,
                        auto_bind=True)

print(f" *** Response from the ldap bind is \n{connection}" )



@app.route('/login', methods=['GET','POST'])
def index():

    # initiate the form..
    form = LoginValidation()

    if request.method in ('POST') :
        login_id = form.user_name_pid.data
        login_password = form.user_pid_Password.data

        # create a directory to hold the Logs
        login_msg = global_ldap_authentication(login_id, login_password)

        # validate the connection
        if login_msg == "Success":
            success_message = f"*** Authentication Success "
            return render_template('success.html', success_message=success_message)

        else:
            error_message = f"*** Authentication Failed - {login_msg}"
            return render_template("error.html", error_message=str(error_message))

    return render_template('login.html', form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
