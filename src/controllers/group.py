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
from model.models import UserActivityEnum, FlashMsgType


def create_group_blueprint(ldapmanager_conn, mongo_handler):
    """
    Creates a blueprint for group-related routes (create, delete, cancel membership).
    """
    group_blueprint = Blueprint('group_blueprint', __name__)

    @group_blueprint.route("/create-group", methods=["GET", "POST"])
    @requires_access_level(ACCESS['admin'])
    def create_group():
        form = GroupCreation()

        # Validate form on POST submission:
        if form.validate_on_submit():
            group_name = form.group_name.data.strip()
            group_description = form.group_description.data.strip()

            # Create the LDAP group with validated data
            ldapmanager_conn.create_group(group_name, group_description)

            # Show success message to the user
            flash(f'Successfully created group: {group_name}!', FlashMsgType.SUCCESS.value)

            # Log the creation activity in MongoDB
            mongo_handler.create_activity(
                activity_enum=UserActivityEnum.CREATE_GROUP, 
                initiator=current_user.id, 
                details={"group": ldapmanager_conn.get_group(group_name)}
            )

            # Redirect after successful POST to prevent form resubmission
            return redirect(url_for('group_blueprint.create_group'))

        # If GET request or form validation failed,
        return render_template('new_object.html', form=form)


    @group_blueprint.route("/delete-group", methods=["POST"])
    @requires_access_level(ACCESS['admin'])
    def delete_group():
        """
        Deletes the given group and logs the action.
        """
        groupe_name = request.form.get('group_name').strip()

        mongo_handler.create_activity(activity_enum=UserActivityEnum.DELETE_GROUP, initiator=current_user.id, details={"group": ldapmanager_conn.get_group(groupe_name)})

        ldapmanager_conn.delete_group(groupe_name)
        flash(f"{groupe_name} has been deleted.", FlashMsgType.INFO.value)

        return redirect(url_for("search_blueprint.search_groups"))

    @group_blueprint.route("/cancel-group", methods=["POST"])
    @requires_access_level(ACCESS['user'])
    def cancel_group():
        """
        Removes a user from a group and logs the action.
        """
        user_name = request.form.get('user_name')
        groupe_name = request.form.get('group_name')

        ldapmanager_conn.cancel_group(user_name, groupe_name)

        mongo_handler.create_activity(activity_enum=UserActivityEnum.CANCEL_GROUP, initiator=current_user.id, details={"group": ldapmanager_conn.get_group(groupe_name), "user": user_name})

        flash(f"{groupe_name} has been removed from user {user_name}.", FlashMsgType.INFO.value)

        return redirect(request.referrer)

    return group_blueprint
