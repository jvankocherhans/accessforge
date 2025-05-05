from flask import Blueprint, jsonify, request, session, redirect, url_for, flash
from flask_login import current_user
from controllers.decorator import requires_access_level
from model.ACCESS import ACCESS

def create_action_blueprint(ldapmanager_conn):
    action_blueprint = Blueprint('action_blueprint', __name__)

    # New API endpoint to remove a group from the cart
    @action_blueprint.route("/remove-group-from-cart", methods=["POST"])
    @requires_access_level(ACCESS['user'])
    def remove_group_from_cart():
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
        usernames = request.form.getlist("usernames")
        groupes = session["cart"]
        print(groupes)
        
        # Print for debugging purposes
        print(f"Assigning users {usernames} to groups {groupes}")

        for username in usernames:
            for groupe in groupes:
                ldapmanager_conn.add_user_to_group(username, groupe)   

        flash(f"Successfully assigned to group!")
        
        session["cart"] = []
        return redirect(url_for("search_blueprint.search_groups"))


    return action_blueprint
