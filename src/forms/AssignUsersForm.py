from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField, FieldList
from wtforms.validators import DataRequired

class AssignUsersForm(FlaskForm):
    usernames = FieldList(HiddenField('Username', validators=[DataRequired()]), min_entries=0)
    groupnames = FieldList(HiddenField('Groupname', validators=[DataRequired()]), min_entries=0)
    submit = SubmitField('Assign Selected Users to All Groups')
