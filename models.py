from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Flight(db.Model):
    __tablename__ = 'flights'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    departure_city_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    arrival_city_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    arrival_date = db.Column(db.Date, nullable=False)

    departure_city = db.relationship('Location', foreign_keys=[departure_city_id], backref='departure_flight')
    arrival_city = db.relationship('Location', foreign_keys=[arrival_city_id], backref='arrival_flight')

def __repr__(self):
        return f'<Flight(id={self.id}, departure_city={self.departure_city.name}, arrival_city={self.arrival_city.name}, departure_date={self.departure_date}, arrival_date={self.arrival_date})>'

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    weathers = db.relationship('Weather', backref='location')

    def __repr__(self):
            return f'<Location(id={self.id}, name={self.name}, latitude={self.latitude}, longitude={self.longitude})>'

class Weather(db.Model):
    __tablename__ = 'weathers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    precipitation = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)

    location = db.relationship('Location', back_populates='weathers')

    def __repr__(self):
        return f'<Weather(id={self.id}, location_id={self.location_id}, date={self.date}, temperature={self.temperature}, precipitation={self.precipitation}, wind_speed={self.wind_speed})>'