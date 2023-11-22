from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, HiddenField, validators, PasswordField, SubmitField
from wtforms.validators import InputRequired , Length, ValidationError, Email   
from datetime import datetime, date

# Check if the data contains only letters and spaces (no special characters or numbers)
def is_valid_string(form, field):
    data = field.data
    if data is None or not data.replace(" ", "").isalpha():
        raise validators.ValidationError('Invalid input. Please enter a valid string.')

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
    departure_location = StringField('From', validators=[is_valid_string, InputRequired(), Length(min=3, max=30)], render_kw={"placeholder": "Airport, City, IATA code (e.g. SEA, JFK, LAX)"})
    arrival_location = StringField('To', validators=[is_valid_string, InputRequired(), Length(min=3, max=30)], render_kw={"placeholder": "Airport, City, IATA code (e.g. SEA, JFK, LAX)"})
    departure_name = HiddenField('Departure name')
    arrival_name = HiddenField('Arrival name')
    departure_iatacode = HiddenField('Departure iatacode')
    arrival_iatacode = HiddenField('Arrival iatacode')
    departure_lat = HiddenField('Departure latitude')
    departure_long = HiddenField('Departure longitude')
    arrival_lat = HiddenField('Arrival latitude')
    arrival_long = HiddenField('Arrival longitude')
    depart_date = DateField('Depart', validators=[is_valid_date, is_future_date, InputRequired()])
    return_date = DateField('Return', validators=[is_valid_date, is_return_date_after_depart_date, InputRequired()])
    passengers = SelectField('Passengers ', validators=[validate_passengers], default=1, choices=[(str(i), str(i)) for i in range(1,10)])


class UserForm(FlaskForm):
    """Form for users sign up and edit."""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    email = StringField('Email', validators=[InputRequired(), Email()])


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])







#     from datetime import datetime
# from flask import Flask, render_template, redirect, flash, session, request, jsonify, g
# from sqlalchemy.exc import IntegrityError
# from forms import FlightForm, UserForm, LoginForm
# from models import db, Flight, Location, User
# from config import SECRET_KEY, CLIENT_ID, CLIENT_SECRET, WEATHER_TOKEN
# import requests

# CURR_USER_KEY = "curr_user"

# # Initialize Flask app
# app = Flask(__name__)

# # Config settings
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flightcast'
# app.config['SECRET_KEY'] = SECRET_KEY
# app.config['SQLALCHEMY_ECHO'] = False
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

# # Init SQLAlchemy
# db.init_app(app)

# try:
#     from seed import seed_database
#     seed_database(app)
# except Exception as e:
#     print(f"Error seeding the database: {e}")

# def safe_commit():
#     try:
#         db.session.commit()
#     except IntegrityError as e:
#         print(f"IntegrityError: {e}")
#         db.session.rollback()
#         raise Exception("Database commit failed.")
#     except Exception as e:
#         print(f"Error: {e}")
#         db.session.rollback()
#         raise Exception("An unknown error occurred.")

# def flash_form_errors(form):
#     for field, errors in form.errors.items():
#         for error in errors:
#             flash(f'{field.capitalize()}: {error}', 'danger')

# @app.route('/', methods=['GET'])
# def home():
#     """Show homepage and list of last saved flights."""
#     fetch_token()
#     session.pop('search_results', None)
#     form = FlightForm()
#     saved_flights = Flight.query.order_by(Flight.id.desc()).limit(5).all()
#     return render_template('home.html', form=form, saved_flights=saved_flights)

# ######################################################################################################################
# # Flight search/show/save/delete  

# @app.route('/submit', methods=['GET', 'POST'])
# def submit_search():
#     """Handle flight search form submission and fetch flight data."""
#     form = FlightForm()
#     if form.is_submitted() and form.validate():
#         flight_form_data = {
#             'originLocationCode': form.departure_iatacode.data,
#             'destinationLocationCode': form.arrival_iatacode.data,
#             'departureDate': form.depart_date.data,
#             'returnDate': form.return_date.data,
#             'adults': form.passengers.data,
#             'max': 25
#         }
#         flight_data = fetch_flights(flight_form_data)
#         departure_name = form.departure_name.data
#         arrival_name = form.arrival_name.data
#         departure_iatacode = form.departure_iatacode.data
#         departure_lat = form.departure_lat.data
#         departure_long = form.departure_long.data
#         arrival_iatacode = form.arrival_iatacode.data
#         arrival_lat = form.arrival_lat.data
#         arrival_long = form.arrival_long.data
#         depart_date = form.depart_date.data
#         return_date = form.return_date.data

#         if not get_location(departure_iatacode):
#             create_location(departure_name, departure_iatacode, departure_lat, departure_long)
#         if not get_location(arrival_iatacode):
#             create_location(arrival_name, arrival_iatacode, arrival_lat, arrival_long)

#         if flight_data:
#             flight_data = unique_flights(flight_data)
#             session['flight_data'] = flight_data
#             return render_template('search_results.html', flight_data=flight_data, departure_name=departure_name, arrival_name=arrival_name, departure_iatacode=departure_iatacode, arrival_iatacode=arrival_iatacode)
#     return redirect('/')

# def fetch_flights(params):
#     """fetch flights."""
#     url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
#     headers = {"Authorization": f"Bearer {session['token']}"}
#     response = requests.get(url, params=params, headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print("Failed to fetch flights.")
#         return None

# def unique_flights(flights):
#     """Remove duplicate flights."""
#     seen = set()
#     unique_flights = []
#     for flight in flights['data']:
#         flight_number = flight['itineraries'][0]['segments'][0]['number']
#         if flight_number not in seen:
#             unique_flights.append(flight)
#             seen.add(flight_number)
#     return {"data": unique_flights}

# @app.route('/flight/<string:flight_id>', methods=['POST'])
# def save_flight(flight_id):
#     """Save selected flight data to the database."""
#     flight_data = session.get('flight_data')
#     if flight_data:
#         matched_flight = next((f for f in flight_data['data'] if f['id'] == flight_id), None)
#         if matched_flight:
#             flight_details = extract_flight_details(matched_flight)
#             location_departure = get_location(flight_details['departure_iatacode'])
#             location_arrival = get_location(flight_details['arrival_iatacode'])
#             new_flight = Flight(
#                 departure_location=location_departure,
#                 arrival_location=location_arrival,
#                 depart_date=datetime.fromisoformat(flight_details['depart_first']),
#                 return_date=datetime.fromisoformat(flight_details['return_last']),
#                 passengers=flight_details['passengers'],
#                 num_stops=flight_details['num_stops'],
#                 total_duration=flight_details['total_duration'],
#                 price=flight_details['price'],
#                 user_id=g.user.id,
#             )
      
#             db.session.add(new_flight)
#             safe_commit()
#             return jsonify({"status": "success", "message": "Flight saved"})
#         else:
#             return jsonify({"status": "failure", "message": "No data found"})
#     else:
#         return jsonify({"status": "failure", "message": "No data in session"})

# def extract_flight_details(matched_flight):
#     itinerary = matched_flight['itineraries'][0]
#     segments = itinerary['segments']

#     if len(segments) > 1:
#         first_segment = segments[0]
#         last_segment = segments[-1]
#     else:
#         first_segment = segments[0]
#         last_segment = segments[0]

#     departure_iatacode = first_segment['departure']['iataCode']
#     arrival_iatacode = last_segment['arrival']['iataCode']
#     depart_first = first_segment['departure']['at']
#     return_last = last_segment['arrival']['at']

#     passengers = len(matched_flight.get('travelerPricings', []))
#     num_stops = len(segments) - 1
#     total_duration = itinerary['duration']
#     price = matched_flight['price']['grandTotal']

#     return {
#         'departure_iatacode': departure_iatacode,
#         'arrival_iatacode': arrival_iatacode,
#         'depart_first': depart_first,
#         'return_last': return_last,
#         'passengers': passengers,
#         'num_stops': num_stops,
#         'total_duration': total_duration,
#         'price': price
#     }

# def get_location(iatacode):
#     location = Location.query.filter_by(iatacode=iatacode).first()
#     return location

# def create_location(name, iatacode, latitude, longitude):
#     location = Location.query.filter_by(iatacode=iatacode).first()
#     if not location:
#         location = Location(name=name, iatacode=iatacode, latitude=latitude, longitude=longitude)
#         db.session.add(location)
#         safe_commit()
#     return location

# @app.route('/flight/<string:flight_id>', methods=['DELETE'])
# def delete_flight(flight_id):
#     """Delete a saved flight by its ID."""
#     flight = Flight.query.get(flight_id)
#     if flight:
#         db.session.delete(flight)
#         safe_commit()
#         return jsonify({"status": "success", "message": "Flight data deleted"})
#     else:
#         return jsonify({"status": "failure", "message": "Flight data not found in session"})
        
# ######################################################################################################################
# # User signup/login/logout and get token for external API

# @app.before_request
# def request_context_setup():
#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])

#         NOT_ALLOWED_PATHS_AUTHED = ['/login', '/signup']
#         if request.path in NOT_ALLOWED_PATHS_AUTHED:
#             flash('Please log out to access this page.', 'danger')
#             return redirect('/')
#     else:
#         g.user = None
#         NOT_ALLOWED_PATHS_UNAUTHED = ['/logout', '/users/profile', '/users/delete']
#         if request.path in NOT_ALLOWED_PATHS_UNAUTHED:
#             flash("Access unauthorized.", "danger")
#             return redirect("/")

# @app.route('/signup', methods=["GET", "POST"])
# def signup():
#     """Handle user signup."""
#     form = UserForm()
#     if form.is_submitted() and form.validate():
#         if User.query.filter_by(username=form.username.data).first():
#             flash("Username already taken", 'danger')
#             return render_template('users/signup.html', form=form)
#         if User.query.filter_by(email=form.email.data).first():
#             flash("Email already taken", 'danger')
#             return render_template('users/signup.html', form=form)
#         user = User.signup(
#             username=form.username.data,
#             password=form.password.data,
#             email=form.email.data,
#         )
#         safe_commit()
#         do_login(user)
#         return redirect("/")
#     return render_template('users/signup.html', form=form)

# @app.route('/login', methods=["GET", "POST"])
# def login():
#     """Handle user login."""
#     form = LoginForm()
#     if form.is_submitted() and form.validate():
#         user = User.authenticate(form.username.data, form.password.data)
#         if user:
#             do_login(user)
#             return redirect("/")
#         flash("Invalid credentials.", 'danger')
#     return render_template('users/login.html', form=form)

# def do_login(user):
#     session[CURR_USER_KEY] = user.id
#     flash(f'Hello, {user.username}.', 'welcome-msg')

# @app.route('/logout', methods=["GET"])
# def logout():
#     """Handle user logout."""
#     if CURR_USER_KEY in session:
#         session.pop(CURR_USER_KEY) 
#     flash(f'Signed out successfully. See you again soon.', 'goodbye-msg')
#     return redirect('/')

# def fetch_token():
#     token_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
#     payload = {
#         'grant_type': 'client_credentials',
#         'client_id': CLIENT_ID,
#         'client_secret': CLIENT_SECRET
#     }
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     response = requests.post(token_url, data=payload, headers=headers)
#     if response.status_code == 200:
#         session["token"] = response.json().get('access_token')
#         return session["token"]
#     else:
#         print("Failed to get token")
#         return None

# @app.route('/token', methods=["GET"])
# def get_token():
#     token = session.get('token')
#     if not token:
#         token = fetch_token() 
#         if not token:
#             return jsonify({"error": "Failed to fetch token"}), 400
#         session['token'] = token
#     return jsonify({"token": token, "weather_token": WEATHER_TOKEN})

# ######################################################################################################################
# # General user routes

# @app.route('/users/<int:user_id>')
# def users_show(user_id):
#     """Display user profile."""
#     if not g.user or g.user.id != user_id:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")
#     user = User.query.get_or_404(user_id)
#     return render_template('users/detail.html', user=user)

# @app.route('/users/profile', methods=["GET", "POST"])
# def profile():
#     """Handle profile update."""
#     form = UserForm()
#     if form.is_submitted() and form.validate():
#         if form.username.data != g.user.username:
#             if User.query.filter(User.username == form.username.data).first():
#                 flash("Username already taken", 'danger')
#                 return redirect ('/users/profile')
#         if form.email.data != g.user.email:
#             if User.query.filter(User.email == form.email.data).first():
#                 flash("Email already taken", 'danger')
#                 return redirect ('/users/profile')
#         user = User.authenticate(g.user.username, form.password.data)
#         if user:
#             g.user.username = form.username.data
#             g.user.email = form.email.data
#             safe_commit()
#             flash(f'Profile updated successfully', 'success')
#             return redirect('/users/profile')

#         else:
#             flash(f'Invalid password', 'danger')
#     return render_template('users/edit.html', form=form)

# @app.route('/users/delete', methods=["POST"])
# def delete_user():
#     """Delete user account."""
#     if g.user:
#         session.pop(CURR_USER_KEY) 
#         db.session.delete(g.user)
#         safe_commit()
#         flash(f'User deleted successfully.', 'goodbye-msg')
#         return redirect('/')
#     else:
#         return jsonify({"error": "User not found"}), 404

# if __name__ == '__main__':
#     app.run(debug=True)




