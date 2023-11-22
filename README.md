# FlightCast

FlightCast is a web application that allows users to search for flights, providing them with options, pricing, and weather forecasts for their destination.

## Getting Started

To get a local copy up and running follow these steps.

### Prerequisites

- Install Python 3.8 or higher: [Python Installation Guide](https://www.python.org/downloads/)
- Install PostgreSQL: [PostgreSQL Installation Guide](https://www.postgresql.org/download/)


### Step 1: Clone the Repository
```bash
git clone https://github.com/solnguyen93/CapstoneProjectOne-FlightCast.git
```

### Step 2: Install Dependencies
```bash
cd CapstoneProjectOne-FlightCast
pip install -r requirements.txt
```

### Step 3: Database Configuration
Ensure PostgreSQL is installed and running. Create a database named 'flightcast':

```bash
createdb flightcast
```

Update the database URI in app.py if necessary. The default is set to 'postgresql:///flightcast'

### Step 4: Set the FLASK_APP environment variable
```bash
export FLASK_APP=app.py
```

### Step 5:  Run the Flask application
```bash
flask run
```

## Using the Provided Configurations

This application comes with a pre-configured `config.py` that contains API keys for immediate use. These are meant for demo purposes and light usage only. Please adhere to the following guidelines:

- Do not use these keys for commercial or heavy personal projects.
- Be mindful that the keys have rate limits, and excessive use may lead to temporary deactivation.
- If you plan to fork this project or use it extensively, consider registering for your own API keys to avoid service interruptions and potential misuse.

## Disclaimer

The API keys provided in this application are for demonstration purposes only. As the owner of these keys, I do not assume responsibility for any misuse or costs incurred. Users are encouraged to obtain their own API keys for prolonged or personal use to ensure security and prevent potential abuse.

## Database Schema

### Flight Table
- **id**: Integer, primary key, autoincrement
- **flight_id**: Integer, not null
- **departure_location_id**: Integer, foreign key (references locations.id), not null
- **arrival_location_id**: Integer, foreign key (references locations.id), not null
- **depart_date**: DateTime, not null
- **return_date**: DateTime, not null
- **passengers**: Integer, not null, default 1
- **num_stops**: Integer, not null, default 0
- **total_duration**: String, not null
- **price**: Float, not null
- **user_id**: Integer, foreign key (references users.id), nullable

### Location Table
- **id**: Integer, primary key, autoincrement
- **name**: Text, not null, unique
- **iatacode**: Text, nullable, unique
- **latitude**: Float, not null
- **longitude**: Float, not null

### User Table
- **id**: Integer, primary key, autoincrement
- **username**: Text, not null, unique
- **password**: Text, not null
- **email**: Text, not null, unique

### Relationships
- **Flight to Location**: Flight.departure_location_id references Location.id
- **Flight to Location**: Flight.arrival_location_id references Location.id
- **User to Flight**: User.id references Flight.user_id

## APIs Used

- **Exchange Rate API**: Provides real-time exchange rates that the server uses for converting prices. `https://api.exchangerate-api.com/v4/latest/EUR`
- **OAuth2 Token**: Used to authenticate API requests for Amadeus. `https://test.api.amadeus.com/v1/security/oauth2/token`
- **Location Data**: Search based on airport or city name. `https://test.api.amadeus.com/v1/reference-data/locations`
- **Flight Offers**: Fetches flight options based on user search parameters. `https://test.api.amadeus.com/v2/shopping/flight-offers` The OAuth2 token is included in the headers of the request to authenticate and authorize access to the Flight Offers API.
  - **Parameters**:
      - originLocationCode (Required): City/airport IATA code from which the traveler will depart (e.g., BOS for Boston).
      - destinationLocationCode (Required): City/airport IATA code to which the traveler is going (e.g., PAR for Paris).
      - departureDate (Required): The date on which the traveler will depart from the origin to go to the destination (in ISO 8601 format, e.g., 2017-12-25).
      - returnDate (Optional): The date on which the traveler will depart from the destination to return to the origin. If not specified, only one-way  - itineraries are found.
      - adults (Required): The number of adult travelers (age 12 or older on the date of departure).
      - max (Optional): Maximum number of flight offers to return.
- **Weather Data**: Provides weather forecast for the destination.
  - **Endpoint**: 
    ```
    https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/${latLong}/${depart}/${returnDate}?unitGroup=us&include=days&key=${weather_token}&contentType=json
    ```
  - **Parameters**:
    - `${latLong}` (Required): Latitude and Longitude of the destination.
    - `${depart}` (Required): Departure date.
    - `${returnDate}` (Required): Return date.
    - `unitGroup=us` (Optional): Unit group set to US for temperature in Fahrenheit.
    - `include=days` (Optional): Include daily weather details.
    - `key=${weather_token}` (Required): API key for authentication.
    - `contentType=json` (Optional): Response format in JSON.

## Frontend Functionality

### Flight Search
- User Input: Users can input their departure and arrival locations, departure and return dates, and the number of passengers.
- API Integration: The application uses the Amadeus API to fetch flight options based on the user's search parameters.
- Display Results: The results include relevant details such as flight duration, stops, and pricing.

### Weather Forecast
- Weather Data: The application provides a weather forecast for the destination.
- Integration: Weather data is obtained from the Visual Crossing Weather API.
- Display: The forecast is displayed alongside the flight options.

### Save and Delete Flights
- User Authentication: Users need to be logged in to save or delete flights.
- Save: Users can save a selected flight, which is then stored in the database.
- Delete: Users can delete a saved flight from their profile.

### User Authentication
- Signup: Users can create an account by providing a unique username, email, and password.
- Login: Existing users can log in using their credentials.
- Logout: Users can log out of their accounts.

### User Profile
- Profile Update: Users can update their username and email.
- Account Deletion: Users can delete their accounts.

## Key Features

### Multiple Levels of Validations
- User’s input > Client-side (JS) validation > Server-side (Python) validation using custom validators with WTForms > Database-side validation at the model level (ORM - SQLAlchemy)

### Focusing on User Experience: Location Suggestions and Their Functionality
- Dynamic Suggestions
- Data-Rich Suggestions
- Scenario 1: Selecting a Suggestion: When a user selects one of these suggestions, not only does it automatically fill in the input field, but the hidden data is also used for various purposes, including external data fetches.
- Scenario 2: Typing Valid Locations: If a user manually types a location, and it matches one of the suggestions without explicitly selecting it, the suggestion list intelligently shows or hides based on the user's interactions with the input field. Meanwhile, the hidden data is seamlessly populated.

### Currency Conversion
- The application converts flight prices from EUR to USD using real-time exchange rates.

### Duplicate Flight Check
- Before saving a flight, the application checks if a similar flight already exists for the user to avoid duplicates.

### Duration Formatting
- The `formatDuration` function converts flight duration from ISO 8601 format (e.g., PT6H28M) to a human-readable format (e.g., 6 hr 28 min).

### Time Formatting
- The `formatTime` function transforms ISO 8601 time (e.g., 2023-10-21T13:03:00) to a readable format (e.g., Oct 21, 2023, 1:03 PM).

### Date Formatting
- The `formatDate` function converts date (e.g., "2024-01-12") to an easier-readable format (e.g., Jan 12, Mon).

### Non-Stop Display
- A functionality that changes the display of the number of stops, replacing "0" with "Non-stop."

