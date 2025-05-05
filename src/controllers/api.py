from flask import Blueprint, jsonify, request, session, redirect, url_for
from flask_login import current_user
from controllers.decorator import requires_access_level
from model.ACCESS import ACCESS

def create_api_blueprint(ldapmanager_conn):
    api_blueprint = Blueprint('api_blueprint', __name__)

    @api_blueprint.route("/api/search-users")
    @requires_access_level(ACCESS['user'])
    def api_search_users():
        search_input = request.args.get("q", "").strip()
        if not search_input:
            return jsonify([])

        users = ldapmanager_conn.search_users(search_input)
        return jsonify([
            {
                "username": user["username"],
                "firstname": user.get("firstname", ""),
                "lastname": user.get("lastname", ""),
                "mail": user.get("mail", ""),
                "phone": user.get("phone", ""),
                "department": user.get("department", "")
            } for user in users
        ])

    # New API endpoint to remove a group from the cart
    @api_blueprint.route("/remove-group", methods=["POST"])
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


    @api_blueprint.route("/bulk-assign-users-to-groups", methods=["POST"])
    @requires_access_level(ACCESS['user'])
    def bulk_assign_users_to_groups():
        usernames = request.form.getlist("usernames")
        groupnames = request.form.getlist("groupnames")
        
        # Print for debugging purposes
        print(f"Assigning users {usernames} to groups {groupnames}")

        for username in usernames:
            for groupname in groupnames:
                ldapmanager_conn.add_user_to_group(username, groupname)  
                

        return redirect(url_for("search_blueprint.groups"))


    return api_blueprint
