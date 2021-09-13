from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length


def is_BGG_valid(form, field):
    for character in field.data:
        if not character.isalpha() and not character.isnumeric() and not character == "_":
            raise ValidationError("Username can only include alphanumeric characters or underscores.")


class GameFinderForm(FlaskForm):
    username = StringField('Board Game Geek Username', validators=[DataRequired(), Length(min=2, max=20), is_BGG_valid])

    numplayers = SelectField('Number of Players', choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    bestonly = BooleanField("Show Best Only")
    minimumcomplexity = SelectField("Minimum Complexity", choices=[0, 1, 2, 3, 4, 5])
    maximumcomplexity = SelectField("Maximum Complexity", choices=[0, 1, 2, 3, 4, 5], default=5)
    hideplayed = BooleanField("Hide Played")
    submit = SubmitField('Find Games!')



