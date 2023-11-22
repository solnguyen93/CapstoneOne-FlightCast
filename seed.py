"""Seed file to make sample data for  db"""
from models import db, Flight, Location, User
from datetime import datetime
from app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


def seed_database(app):
    app.app_context().push()
    with app.app_context():
        db.drop_all() 
        db.create_all()

        location_departure = Location(name='SEATTLE-TACOMA INTERNATIONAL AIRPORT', iatacode='SEA', latitude=47.4502, longitude=-122.3088)
        location_arrival = Location(name='LOS ANGELES INTERNATIONAL AIRPORT', iatacode='LAX', latitude=33.9416, longitude=-118.4085)
        location_arrival_2 = Location(name='CANCUN INTERNATIONAL AIRPORT', iatacode='CUN', latitude=21.0428, longitude=-86.8736)

        db.session.add(location_departure)
        db.session.add(location_arrival)
        db.session.add(location_arrival_2)
        db.session.commit()

        hashed_pwd = bcrypt.generate_password_hash("ssssss").decode('UTF-8')
        user1 = User(
            username="aaa",
            password=hashed_pwd,
            email="aaa.ssssss@example.com"
        )

        db.session.add(user1)
        db.session.commit()

        flight1 = Flight(
            flight_id=1,
            departure_location_id=1,
            arrival_location_id=2,
            depart_date=datetime(2023, 10, 25, 14, 30),
            return_date=datetime(2023, 10, 26, 16, 45), 
            passengers=1,
            num_stops=0,
            total_duration='PT04H10M',
            price=289.71,    # EUR - JS will convert to USD
            user_id=user1.id
        )

        flight2 = Flight(
            flight_id=2,
            departure_location_id=1,
            arrival_location_id=3,
            depart_date=datetime(2023, 11, 4, 6, 0),
            return_date=datetime(2023, 12, 11, 8, 15),
            passengers=2,
            num_stops=1,
            total_duration='PT14H10M',
            price=2745.6,    # EUR
            user_id=user1.id
        )

        db.session.add(flight1)
        db.session.add(flight2)
        db.session.commit()
