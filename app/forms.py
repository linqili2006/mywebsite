from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    passwd = StringField('passwd', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
