from flask import Blueprint
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

from flask import render_template, request, redirect, url_for, flash
from forms.GroupForm import *
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer

from controllers.decorator import requires_access_level
from model.ACCESS import ACCESS

def create_group_blueprint(ldapmanager_conn):
  group_blueprint = Blueprint('group_blueprint', __name__)
  
  
  @group_blueprint.route("/create-group", methods=["GET", "POST"])
  @requires_access_level(ACCESS['admin'])
  def create_group():
      form = GroupCreation()

      if request.method in ('POST') :
          group_name = form.group_name.data
          group_description = form.group_description.data
          
          print(group_name)
          print(group_description)

          print(ldapmanager_conn.create_group(group_name, group_description))
          
          flash(f'Successfully created group: {group_name}!')
          
          return render_template('test/test_group_creation.html', form=form)
          
      return render_template('test/test_group_creation.html', form=form)
  
  return group_blueprint