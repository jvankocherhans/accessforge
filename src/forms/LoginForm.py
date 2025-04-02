from flask_wtf import FlaskForm  # FlaskForm statt Form verwenden
from wtforms import StringField, PasswordField, validators


class LoginValidation(FlaskForm):  # FlaskForm verwenden
    user_name = StringField('', [validators.DataRequired()],
                                render_kw={'autofocus': True, 'placeholder': 'Enter User'})

    user_password = PasswordField('', [validators.DataRequired()],
                                      render_kw={'autofocus': True, 'placeholder': 'Enter your login Password'})
