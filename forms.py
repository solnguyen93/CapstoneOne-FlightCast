from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length   

class FlightForm (FlaskForm):
    """Form for searching flights"""
    departure_city = StringField('Departure City', validators=[InputRequired(), Length(max=30)]) 
    arrival_city = StringField('Arrival City', validators=[InputRequired(), Length(max=30)]) 
    departure_date = StringField('Departure Date', validators=[InputRequired(), Length(max=30)]) 
    arrival_date = StringField('Arrival Date', validators=[InputRequired(), Length(max=30)]) 
