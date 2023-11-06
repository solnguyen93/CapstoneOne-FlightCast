# FlightCast

FlightCast is a web application that allows users to search for flights, providing them with options, pricing, and weather forecasts for their destination.

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

- Install Python 3.8 or higher: [Python Installation Guide](https://www.python.org/downloads/)
- Install PostgreSQL: [PostgreSQL Installation Guide](https://www.postgresql.org/download/)

```bash
# Step 1: Clone the Repository
git clone https://github.com/solnguyen93/CapstoneProjectOne-FlightCast.git
cd CapstoneProjectOne-FlightCast

# Step 2: Install Dependencies
pip install -r requirements.txt

# Step 3: Database Configuration
# Ensure PostgreSQL is installed and running
# Create a database named 'flightcast':
createdb flightcast

# Update the database URI in app.py if necessary
# The default is set to 'postgresql:///flightcast'

# Set the FLASK_APP environment variable
export FLASK_APP=app.py

# Run the Flask application
flask run
```

## Using the Provided Configurations

This application comes with a pre-configured `config.py` that contains API keys for immediate use. These are meant for demo purposes and light usage only. Please adhere to the following guidelines:

- Do not use these keys for commercial or heavy personal projects.
- Be mindful that the keys have rate limits, and excessive use may lead to temporary deactivation.
- If you plan to fork this project or use it extensively, consider registering for your own API keys to avoid service interruptions and potential misuse.

## Disclaimer

The API keys provided in this application are for demonstration purposes only. As the owner of these keys, I do not assume responsibility for any misuse or costs incurred. Users are encouraged to obtain their own API keys for prolonged or personal use to ensure security and prevent potential abuse.

## Backend Functionality

- **Currency Conversion**: The server uses the ExchangeRate-API to convert prices from EUR to the user's preferred currency. This feature ensures that users have an accurate estimate of cost in their local currency.

## APIs Used

- **Flight Offers**: Fetches flight options based on user search parameters. `https://test.api.amadeus.com/v2/shopping/flight-offers`
- **OAuth2 Token**: Used to authenticate API requests. `https://test.api.amadeus.com/v1/security/oauth2/token`
- **Location Data**: Powers the airport and city name search feature. `https://test.api.amadeus.com/v1/reference-data/locations`
- **Exchange Rate API**: Provides real-time exchange rates that the server uses for converting prices. `https://api.exchangerate-api.com/v4/latest/EUR`



