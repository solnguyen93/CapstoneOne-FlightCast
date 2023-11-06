from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

class Flight(db.Model):
    __tablename__ = 'flights'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    departure_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    arrival_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    depart_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)
    passengers = db.Column(db.Integer, nullable=False, default=1)
    num_stops = db.Column(db.Integer, nullable=False, default=0)
    total_duration = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    departure_location = db.relationship('Location', foreign_keys=[departure_location_id], backref='departure_flight')
    arrival_location = db.relationship('Location', foreign_keys=[arrival_location_id], backref='arrival_flight')


    def __repr__(self):
        return f'<Flight_id={self.id}, depart_date={self.depart_date}, return_date={self.return_date}, passengers={self.passengers}, num_stops={self.num_stops}, total_duration={self.total_duration}, price={self.price})>'


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.Text, nullable=False)
    # latitude = db.Column(db.Float, nullable=False)
    # longitude = db.Column(db.Float, nullable=False)

    weather = db.relationship('Weather', backref='location')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    flights = db.relationship('Flight', backref='user', lazy=True)


    def __repr__(self):
        return f"<User_id={self.id}, username={self.username}, email={self.email}, num_flights={len(self.flights)}>"

    @classmethod
    def signup(cls, username, password, email):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            email=email,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Weather(db.Model):
    __tablename__ = 'weathers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    # temperature = db.Column(db.Float, nullable=False)
    # precipitation = db.Column(db.Float, nullable=False)
    # wind_speed = db.Column(db.Float, nullable=False)