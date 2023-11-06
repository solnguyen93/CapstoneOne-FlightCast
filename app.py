from datetime import datetime
from flask import Flask, render_template, redirect, flash, session, request, jsonify, g
from sqlalchemy.exc import IntegrityError
from forms import FlightForm, UserForm, LoginForm
from models import db, Flight, Location, Weather, User
from config import SECRET_KEY, CLIENT_ID, CLIENT_SECRET
import requests

CURR_USER_KEY = "curr_user"

# Initialize Flask app
app = Flask(__name__)

# Config settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flightcast'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

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
    """Show homepage and list of last saved flights."""
    session.pop('search_results', None)
    form = FlightForm()
    saved_flights = Flight.query.order_by(Flight.id.desc()).limit(5).all()
    return render_template('home.html', form=form, saved_flights=saved_flights)


@app.route('/get-cities<string:userInput>', methods=['GET', 'POST'])
def get_city_code():
    """Handle flight search form submission and fetch flight data."""
    form = FlightForm()
    if form.is_submitted() and form.validate():
        form_data = {
            'originLocationCode': form.departure_location.data,
            'destinationLocationCode': form.arrival_location.data,
            'departureDate': form.depart_date.data,
            'returnDate': form.return_date.data,
            'adults': form.passengers.data,
            'max': 25
        }
        flight_data = fetch_flights(form_data)
        if flight_data:
            session['cities'] = flight_data
            return render_template('search_results.html', flight_data=flight_data)
        else:
            return jsonify({"status": "error", "message": "Failed to fetch flights"})
    return jsonify({"status": "error", "message": "Error in flight search."})

def fetch_cities(params):
    """fetch cities."""
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    headers = {"Authorization": f"Bearer {session['token']}"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch flight destinations")
        return None


######################################################################################################################
# Flight search/show/save/delete  

@app.route('/submit', methods=['GET', 'POST'])
def submit_search():
    """Handle flight search form submission and fetch flight data."""
    form = FlightForm()
    if form.is_submitted() and form.validate():
        form_data = {
            'originLocationCode': form.departure_location.data,
            'destinationLocationCode': form.arrival_location.data,
            'departureDate': form.depart_date.data,
            'returnDate': form.return_date.data,
            'adults': form.passengers.data,
            'max': 25
        }
        flight_data = fetch_flights(form_data)
        if flight_data:
            flight_data = unique_flights(flight_data)
            session['flight_data'] = flight_data
            return render_template('search_results.html', flight_data=flight_data)
        else:
            return jsonify({"status": "error", "message": "Failed to fetch flights"})
    return jsonify({"status": "error", "message": "Error in flight search."})

def fetch_flights(params):
    """fetch flights."""
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {session['token']}"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch flight destinations")
        return None

def unique_flights(flights):
    """Remove duplicate flights."""
    seen = set()
    unique_flights = []
    for flight in flights['data']:
        flight_number = flight['itineraries'][0]['segments'][0]['number']
        if flight_number not in seen:
            unique_flights.append(flight)
            seen.add(flight_number)
    return {"data": unique_flights}

@app.route('/flight/<string:flight_id>', methods=['POST'])
def save_flight(flight_id):
    """Save selected flight data to the database."""
    flight_data = session.get('flight_data')
    if flight_data:
        matched_flight = next((f for f in flight_data['data'] if f['id'] == flight_id), None)
        if matched_flight:
            flight_details = extract_flight_details(matched_flight)
            location_departure = get_or_create_location(flight_details['departure_location'])
            location_arrival = get_or_create_location(flight_details['arrival_location'])
            new_flight = Flight(
                departure_location=location_departure,
                arrival_location=location_arrival,
                depart_date=datetime.fromisoformat(flight_details['depart_first']),
                return_date=datetime.fromisoformat(flight_details['return_last']),
                passengers=flight_details['passengers'],
                num_stops=flight_details['num_stops'],
                total_duration=flight_details['total_duration'],
                price=flight_details['price'],
                user_id=g.user.id,
            )
      
            db.session.add(new_flight)
            safe_commit()
            return jsonify({"status": "success", "message": "Flight saved"})
        else:
            return jsonify({"status": "failure", "message": "No data found"})
    else:
        return jsonify({"status": "failure", "message": "No data in session"})

def extract_flight_details(matched_flight):
    itinerary = matched_flight['itineraries'][0]
    segments = itinerary['segments']

    if len(segments) > 1:
        first_segment = segments[0]
        last_segment = segments[-1]
    else:
        first_segment = segments[0]
        last_segment = segments[0]

    departure_location = first_segment['departure']['iataCode']
    arrival_location = last_segment['arrival']['iataCode']
    depart_first = first_segment['departure']['at']
    return_last = last_segment['arrival']['at']

    passengers = len(matched_flight.get('travelerPricings', []))
    num_stops = len(segments) - 1
    total_duration = itinerary['duration']
    price = matched_flight['price']['grandTotal']

    return {
        'departure_location': departure_location,
        'arrival_location': arrival_location,
        'depart_first': depart_first,
        'return_last': return_last,
        'passengers': passengers,
        'num_stops': num_stops,
        'total_duration': total_duration,
        'price': price
    }

def get_or_create_location(location_code):
    location = Location.query.filter_by(code=location_code).first()
    if not location:
        location = Location(code=location_code)
        db.session.add(location)
        safe_commit()
    return location

@app.route('/flight/<string:flight_id>', methods=['DELETE'])
def delete_flight(flight_id):
    """Delete a saved flight by its ID."""
    flight = Flight.query.get(flight_id)
    if flight:
        db.session.delete(flight)
        safe_commit()
        return jsonify({"status": "success", "message": "Flight data deleted"})
    else:
        return jsonify({"status": "failure", "message": "Flight data not found in session"})
        
######################################################################################################################
# User signup/login/logout and get token for external API

@app.before_request
def add_user_to_g():
    fetch_token()
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

        NOT_ALLOWED_PATHS = ['/login', '/signup']
        if request.path in NOT_ALLOWED_PATHS:
            flash('Please log out to access this page.', 'danger')
            return redirect('/login')
    else:
        g.user = None

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
    """Handle user signup."""
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
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    do_logout()
    return redirect('/')

def do_logout():
    session.clear()
    flash(f'Signed out successfully. See you again soon.', 'welcome-msg')

def fetch_token():
    if "token" in session:
        return session["token"]
    else:
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
    token = fetch_token()
    return jsonify({"token": token}) if token else (jsonify({"error": "Failed to fetch token"}), 400)

######################################################################################################################
# General user routes
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Display user profile."""
    if not g.user or g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)

@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Handle profile update."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
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
            return jsonify({"status": "success", "message": "Profile updated successfully"})
        else:
            return jsonify({"status": "failure", "message": "Error updating profile"})
    return render_template('users/edit.html', form=form)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user account."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        do_logout()
        db.session.delete(g.user)
        safe_commit()
        return redirect('/')
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run()




