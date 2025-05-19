from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, DateField, SubmitField
from wtforms.validators import Optional
from model.models import UserActivityEnum

class ActivityFilterForm(FlaskForm):
    activity = SelectField(
        "Activity",
        choices=[("", "All")] + [(e.value, e.value) for e in UserActivityEnum],
        validators=[Optional()]
    )
    initiator = StringField("Initiator", validators=[Optional()])
    date_from = DateField("Start Date", format="%Y-%m-%d", validators=[Optional()])
    date_to = DateField("End Date", format="%Y-%m-%d", validators=[Optional()])
    submit = SubmitField("Filter")
