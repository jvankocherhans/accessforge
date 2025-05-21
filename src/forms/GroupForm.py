from flask_wtf import FlaskForm
from wtforms import StringField, validators

class GroupCreation(FlaskForm):
    group_name = StringField(
        '',
        [
            validators.DataRequired(),
            validators.Length(max=64, message="Group name must be at most 64 characters long."),
            validators.Regexp(
                r'^[a-zA-Z0-9._\-](?:[a-zA-Z0-9._\-\s]*[a-zA-Z0-9._\-])?$',
                message="Group name may contain letters, digits, dashes, underscores, dots and spaces, but not start or end with a space."
            )
        ],
        render_kw={'autofocus': True, 'placeholder': 'Enter groupname'}
    )

    group_description = StringField(
        '',
        [
            validators.DataRequired(),
            validators.Length(max=255, message="Description must be at most 255 characters long."),
            validators.Regexp(
                r'^\S(?:.*\S)?$',
                message="Description must not start or end with a space."
            )
        ],
        render_kw={'placeholder': 'Enter groupdescription'}
    )
