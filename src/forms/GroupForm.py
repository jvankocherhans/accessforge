from flask_wtf import FlaskForm  # FlaskForm statt Form verwenden
from wtforms import StringField, PasswordField, validators


class GroupCreation(FlaskForm):  # FlaskForm verwenden
  group_name = StringField('',[validators.DataRequired()], render_kw={'autofocus': True, 'placeholder': 'Gruppennamen eingeben'})

  group_description = group_name = StringField('',[validators.DataRequired()], render_kw={'autofocus': True, 'placeholder': 'Gruppenbeschreibung eingeben'})