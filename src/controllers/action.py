from flask import Blueprint, jsonify, request, session, redirect, url_for, flash, render_template
from flask_login import current_user
from controllers.decorator import requires_access_level
from model.ACCESS import ACCESS
from model.models import Activity, UserActivityEnum, FlashMsgType
from forms.ActivityForm import ActivityFilterForm
from datetime import datetime, timedelta

def create_action_blueprint(ldapmanager_conn, mongo_handler):
    """
    Blueprint for handling cart actions, bulk user-group assignments, and activity logs.
    """
    action_blueprint = Blueprint('action_blueprint', __name__)

    @action_blueprint.route("/remove-group-from-cart", methods=["POST"])
    @requires_access_level(ACCESS['user'])
    def remove_group_from_cart():
        """
        Removes a group from the session cart by groupname.
        """
        groupname_to_remove = request.form.get('remove_group')
        if groupname_to_remove:
            cart = session.get('cart', [])
            # Remove the group from the cart by groupname
            cart = [group for group in cart if group["groupname"] != groupname_to_remove]
            session['cart'] = cart
                        
            return redirect(url_for('search_blueprint.shopping_cart'))

        return redirect(url_for('search_blueprint.shopping_cart'))


    @action_blueprint.route("/bulk-assign-users-to-groups", methods=["POST"])
    @requires_access_level(ACCESS['user'])
    def bulk_assign_users_to_groups():
        """
        Assigns selected users to all groups in the session cart.
        Clears the cart and logs the action.
        """
        usernames = request.form.getlist("usernames")
        groups = session["cart"]

        for username in usernames:
            for group in groups:
                ldapmanager_conn.add_user_to_group(username, group)   

        flash(f"Successfully assigned to group!", FlashMsgType.SUCCESS)
        
        session["cart"] = []
        
        mongo_handler.create_activity(activity_enum=UserActivityEnum.ASSIGN, initiator=current_user.id, details={"users": usernames, "groups":groups})
        
        return redirect(url_for("search_blueprint.search_groups"))
    

    @action_blueprint.route("/activity", methods=["GET", "POST"])
    @requires_access_level(ACCESS['admin'])
    def show_activity():
        """
        Displays a filtered list of user activities based on form inputs or URL parameters.
        """
        form = ActivityFilterForm()

        activity_type = request.args.get('activity') or form.activity.data
        initiator = request.args.get('initiator') or form.initiator.data
        date_from = request.args.get('date_from') or form.date_from.data
        date_to = request.args.get('date_to') or form.date_to.data

        query = Activity.objects()

        if activity_type:
            query = query.filter(activity=activity_type)
        if initiator:
            query = query.filter(initiator__icontains=initiator)
        if date_from:
            query = query.filter(datetime__gte=datetime.strptime(date_from, "%Y-%m-%d"))
        if date_to:
            end_of_day = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(datetime__lte=end_of_day)

        query = query.order_by('-datetime')

        return render_template("activity.html", activities=query, form=form)


    return action_blueprint
