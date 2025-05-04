from flask import redirect, flash, request
from flask_login import current_user
from functools import wraps

def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect('/login')

            #user = User.query.filter_by(id=current_user.id).first()

            if not current_user.allowed(access_level):
                flash('You do not have access to this resource.')
                return redirect(request.referrer)
            return f(*args, **kwargs)
        return decorated_function
    return decorator