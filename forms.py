from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, SelectField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(2,80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(6,128)])
    confirm = PasswordField("Confirm", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class TripForm(FlaskForm):
    destination = StringField("Destination", validators=[DataRequired()])
    start_date = DateField("Start date", validators=[DataRequired()], format="%Y-%m-%d")
    end_date = DateField("End date", validators=[DataRequired()], format="%Y-%m-%d")
    travelers = IntegerField("Travelers", validators=[DataRequired(), NumberRange(min=1)])
    budget_preference = SelectField("Budget preference", choices=[("low","Low"),("medium","Medium"),("high","High")])
    summary = TextAreaField("Summary")
    submit = SubmitField("Save Trip")

class ActivityForm(FlaskForm):
    activity_name = StringField("Activity", validators=[DataRequired()])
    cost = FloatField("Cost", validators=[DataRequired()])
    category = StringField("Category")
    submit = SubmitField("Add Activity")
