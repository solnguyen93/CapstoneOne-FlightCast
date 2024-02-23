from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, HiddenField, validators, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from datetime import datetime, date

# Check if the data contains only letters and spaces (no special characters or numbers)


def is_valid_string(form, field):
    data = field.data
    if data is None or not data.replace(" ", "").isalpha():
        raise validators.ValidationError(
            'Invalid input. Please enter a valid string.')

# Check if date is valid (user input date format mm/dd/yyyy, by default, it will sent to the server as yyyy/mm/dd as part of the HTTP request)


def is_valid_date(form, field):
    data = field.data
    if not isinstance(data, date):  # Check if data is not a date object
        raise ValidationError('Invalid date format. Please use yyyy-mm-dd')


def validate_passengers(form, field):
    if int(field.data) < 1 or int(field.data) > 9:
        raise ValidationError('Number of passengers must be between 1 and 9.')

# Check if depart it tomorrow or later


def is_future_date(form, field):
    today = date.today()
    if field.data <= today:
        raise ValidationError('Departure date must be tomorrow or later.')

# Check if return date is after depart


def is_return_date_after_depart_date(form, field):
    depart_date = form.depart_date.data
    return_date = field.data
    if return_date <= depart_date:
        raise ValidationError('Return date must be after departure date.')


class FlightForm (FlaskForm):
    """Form for searching flights"""
    departure_location = StringField('From', validators=[is_valid_string, InputRequired(), Length(
        min=3, max=30)], render_kw={"placeholder": "Airport, City, IATA code (e.g. SEA, JFK, LAX)"})
    arrival_location = StringField('To', validators=[is_valid_string, InputRequired(), Length(
        min=3, max=30)], render_kw={"placeholder": "Airport, City, IATA code (e.g. SEA, JFK, LAX)"})
    departure_name = HiddenField('Departure name')
    arrival_name = HiddenField('Arrival name')
    departure_iatacode = HiddenField('Departure iatacode')
    arrival_iatacode = HiddenField('Arrival iatacode')
    departure_lat = HiddenField('Departure latitude')
    departure_long = HiddenField('Departure longitude')
    arrival_lat = HiddenField('Arrival latitude')
    arrival_long = HiddenField('Arrival longitude')
    depart_date = DateField('Depart', validators=[
                            is_valid_date, is_future_date, InputRequired()])
    return_date = DateField('Return', validators=[
                            is_valid_date, is_return_date_after_depart_date, InputRequired()])
    passengers = SelectField('Passengers ', validators=[
                             validate_passengers], default=1, choices=[(str(i), str(i)) for i in range(1, 10)])


class UserForm(FlaskForm):
    """Form for users sign up and edit."""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=6)])
    email = StringField('Email', validators=[InputRequired(), Email()])


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=6)])
