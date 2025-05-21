from flask import redirect, flash, request, url_for, render_template
from flask_login import current_user
from functools import wraps
from model.models import FlashMsgType

def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("user_blueprint.login"))
            
            if not current_user.allowed(access_level):
                flash("You do not have access to this resource.", FlashMsgType.ERROR.value)
                return render_template("no_permission.html")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_access():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated and request.endpoint == "user_blueprint.login": 
                return redirect(url_for("search_blueprint.search")) 
            return f(*args, **kwargs)
        return decorated_function
    return decorator