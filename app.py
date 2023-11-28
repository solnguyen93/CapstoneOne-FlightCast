from flask import Flask, render_template, redirect, flash, session, request, jsonify, g
from sqlalchemy.exc import IntegrityError
from forms import FlightForm, UserForm, LoginForm
from models import db, Flight, Location, User
from dotenv import load_dotenv
import requests
import os

CURR_USER_KEY = "curr_user"

# Initialize Flask app
app = Flask(__name__)

# Config settings
if os.getenv('FLASK_ENV') == 'development': # Check if running in a local development environment
    load_dotenv('environment.env')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = 'test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')

# Init SQLAlchemy
db.init_app(app)

try:
    from seed import seed_database
    seed_database(app)
except Exception as e:
    print(f"Error seeding the database: {e}")

def safe_commit():
    try:
        db.session.commit()
    except IntegrityError as e:
        print(f"IntegrityError: {e}")
        db.session.rollback()
        raise Exception("Database commit failed.")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
        raise Exception("An unknown error occurred.")

def flash_form_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field.capitalize()}: {error}', 'danger')

@app.route('/', methods=['GET'])
def home():
    """Show homepage and list of saved flights if logged in."""
    fetch_token()
    session.pop('search_results', None)
    form = FlightForm()
    if g.user:
        saved_flights = Flight.query.filter_by(user_id=g.user.id).order_by(Flight.id.desc()).all()
    else:
        saved_flights = []
    return render_template('home.html', form=form, saved_flights=saved_flights)

def fetch_token():
    """Request token from API"""
    token_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code == 200:
        session["token"] = response.json().get('access_token')
        return session["token"]
    else:
        print("Failed to get token")
        return None

@app.route('/token', methods=["GET"])
def get_token():
    """Get token for API"""
    token = session.get('token')
    if not token:
        token = fetch_token() 
        if not token:
            return jsonify({"error": "Failed to fetch token"}), 400
        session['token'] = token
    return jsonify({"token": token, "weather_token": WEATHER_TOKEN})

######################################################################################################################
# Flight search/show/save/delete  

@app.route('/submit', methods=['GET', 'POST'])
def submit_search():
    """Handle flight search form submission and server-side validation"""
    form = FlightForm()
    if form.is_submitted() and form.validate():
        flight_form_data = {
            'originLocationCode': form.departure_iatacode.data,
            'destinationLocationCode': form.arrival_iatacode.data,
            'departureDate': form.depart_date.data,
            'returnDate': form.return_date.data,
            'adults': form.passengers.data,
            'max': 25
        }
        flight_data = fetch_flights(flight_form_data)
        departure_name = form.departure_name.data
        arrival_name = form.arrival_name.data
        departure_iatacode = form.departure_iatacode.data
        departure_lat = form.departure_lat.data
        departure_long = form.departure_long.data
        arrival_iatacode = form.arrival_iatacode.data
        arrival_lat = form.arrival_lat.data
        arrival_long = form.arrival_long.data
        depart_date = form.depart_date.data
        return_date = form.return_date.data
        passengers = form.passengers.data
        session['departure_name'] = departure_name
        session['departure_iatacode'] = departure_iatacode
        session['departure_lat'] = departure_lat
        session['departure_long'] = departure_long
        session['arrival_name'] = arrival_name
        session['arrival_iatacode'] = arrival_iatacode
        session['arrival_lat'] = arrival_lat
        session['arrival_long'] = arrival_long
        session['depart_date'] = depart_date
        session['return_date'] = return_date
        session['passengers'] = passengers
        if flight_data:
            flight_data = filter_flights(flight_data, departure_iatacode)
            return render_template('search_results.html', 
                flight_data=flight_data, 
                departure_name=departure_name,
                departure_iatacode=departure_iatacode, 
                arrival_name=arrival_name,
                arrival_iatacode=arrival_iatacode)
    return redirect('/')

def fetch_flights(params):
    """Fetch flights."""
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {session['token']}"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch flights.")
        return None

def filter_flights(flights, iatacode):
    """Remove duplicate flights."""
    seen = set()
    filter_flights = []
    for flight in flights['data']:
        flight_number = flight['itineraries'][0]['segments'][0]['number']
        departure_iatacode = flight['itineraries'][0]['segments'][0]['departure']['iataCode']
        if flight_number not in seen and departure_iatacode == iatacode:
            filter_flights.append(flight)
            seen.add(flight_number)
        
    return {"data": filter_flights}

@app.route('/save_flight', methods=['POST'])
def save_flight():
    """Save selected flight to the database."""
    flight_details = request.json  # Assuming data is sent as JSON in the request
    if not g.user:
        return jsonify({"status": "failure", "message": "User not authenticated"})

    if flight_details:
        location_departure = get_location(session['departure_iatacode'])
        location_arrival = get_location(session['arrival_iatacode'])

        if not location_departure:
            location_departure = create_location(session['departure_name'], session['departure_iatacode'], session['departure_lat'], session['departure_long'])

        if not location_arrival:
            location_arrival = create_location(session['arrival_name'], session['arrival_iatacode'], session['arrival_lat'], session['arrival_long'])

        existing_flight = Flight.query.filter_by(
            flight_id=flight_details['flight_id'],
            departure_location=location_departure,
            arrival_location=location_arrival,
            depart_date=session['depart_date'],
            return_date=session['return_date'],
            passengers=session['passengers'],
            num_stops=flight_details['numStopsValue'],
            total_duration=flight_details['durationValue'],
            price=flight_details['priceValue'],
            user_id=g.user.id
        ).first()

        if existing_flight:
            return jsonify({"status": "failure", "message": "Similar flight already exists for the user"})

        new_flight = Flight(
            flight_id=flight_details['flight_id'],
            departure_location=location_departure,
            arrival_location=location_arrival,
            depart_date=session['depart_date'],
            return_date=session['return_date'],
            passengers=session['passengers'],
            num_stops=flight_details['numStopsValue'],
            total_duration=flight_details['durationValue'],
            price=flight_details['priceValue'],
            user_id=g.user.id
        )

        db.session.add(new_flight)
        safe_commit()
        return jsonify({"status": "success", "message": "Flight saved"})
    else:
        return jsonify({"status": "failure", "message": "No data received in the request"})

def get_location(iatacode):
    location = Location.query.filter_by(iatacode=iatacode).first()
    return location

def create_location(name, iatacode, latitude, longitude):
    location = Location(name=name, iatacode=iatacode, latitude=latitude, longitude=longitude)
    db.session.add(location)
    safe_commit()
    return location

@app.route('/flight/<int:id>', methods=['DELETE'])
def delete_flight(id):
    """Delete a saved flight by its ID."""
    flight = Flight.query.get(id)
    if flight:
        db.session.delete(flight)
        safe_commit()
        return jsonify({"status": "success", "message": "Flight data deleted"})
    else:
        return jsonify({"status": "failure", "message": "Flight data not found in session"})
        
######################################################################################################################
# User signup/login/logout

@app.before_request
def request_context_setup():
    """Handle page authorization."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

        NOT_ALLOWED_PATHS_AUTHED = ['/login', '/signup']
        if request.path in NOT_ALLOWED_PATHS_AUTHED:
            flash('Please log out to access this page.', 'danger')
            return redirect('/')
    else:
        g.user = None
        NOT_ALLOWED_PATHS_UNAUTHED = ['/logout', '/users/profile', '/users/delete']
        if request.path in NOT_ALLOWED_PATHS_UNAUTHED:
            flash("Access unauthorized.", "danger")
            return redirect("/")

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup."""
    form = UserForm()
    if form.is_submitted() and form.validate():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already taken", 'danger')
            return render_template('users/signup.html', form=form)
        user = User.signup(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
        )
        safe_commit()
        do_login(user)
        return redirect("/")
    return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    form = LoginForm()
    if form.is_submitted() and form.validate():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            return redirect("/")
        flash("Invalid credentials.", 'danger')
    return render_template('users/login.html', form=form)

def do_login(user):
    session[CURR_USER_KEY] = user.id
    flash(f'Hello, {user.username}.', 'welcome-msg')

@app.route('/logout', methods=["GET"])
def logout():
    """Handle user logout."""
    if CURR_USER_KEY in session:
        session.pop(CURR_USER_KEY) 
    flash(f'Signed out successfully. See you again soon.', 'goodbye-msg')
    return redirect('/')

######################################################################################################################
# General user routes

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Display user profile."""
    if not g.user or g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = User.query.get_or_404(user_id)
    return render_template('users/detail.html', user=user)

@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Handle profile update."""
    form = UserForm()
    if form.is_submitted() and form.validate():
        if form.username.data != g.user.username:
            if User.query.filter(User.username == form.username.data).first():
                flash("Username already taken", 'danger')
                return redirect ('/users/profile')
        if form.email.data != g.user.email:
            if User.query.filter(User.email == form.email.data).first():
                flash("Email already taken", 'danger')
                return redirect ('/users/profile')
        user = User.authenticate(g.user.username, form.password.data)
        if user:
            g.user.username = form.username.data
            g.user.email = form.email.data
            safe_commit()
            flash(f'Profile updated successfully', 'success')
            return redirect('/users/profile')

        else:
            flash(f'Invalid password', 'danger')
    return render_template('users/edit.html', form=form)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user account."""
    if g.user:
        session.pop(CURR_USER_KEY) 
        db.session.delete(g.user)
        safe_commit()
        flash(f'User deleted successfully.', 'goodbye-msg')
        return redirect('/')
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=False)