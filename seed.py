"""Seed file to make sample data for  db"""
from models import db, User, Feedback
from app import app

app.app_context().push()

with app.app_context():
    db.drop_all() 
    db.create_all()

    user1 = User(username='user1', password='user1', email='user1@example.com', first_name='user1', last_name='user1' )
    user2 = User(username='user2', password='user2', email='user2@example.com', first_name='user2', last_name='user2' )
    db.session.add(user1)
    db.session.add(user2)

    feedback1 = Feedback(title='Feedback 1 Title', content='Feedback 1 Content', user_username='user1')
    feedback2 = Feedback(title='Feedback 2 Title', content='Feedback 2 Content', user_username='user1')
    feedback3= Feedback(title='Feedback 3 Title', content='Feedback 3 Content', user_username='user2')
    db.session.add(feedback1)
    db.session.add(feedback2)
    db.session.add(feedback3)

    db.session.commit()
