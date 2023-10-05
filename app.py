
from flask import Flask, render_template, redirect, flash, session, request, jsonify
from forms import FlightForm
from models import Flight, Location, Weather

# Create a Flask application instance
app = Flask(__name__)

# App configuration settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flightcast'
app.config['SECRET_KEY'] = 'secret_key_here'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Initialize SQLAlchemy with the Flask app
db.init_app(app)

@app.route('/')
def home():
    """Home"""
    return render_template('home.html')





# exempt_routes = ['home', 'login','register']

# @app.before_request
# def check_login():
#     # Check if the user is not logged in and the current request is not for an exempt route
#     if request.endpoint not in exempt_routes:
#         if 'username' not in session:
#             flash('Please login first.', 'danger')
#             return redirect('/login')

# @app.route('/')
# def home():
#     """Home"""
#     return render_template('home.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     """Handles user registration"""
#     # Check if the user is already logged in, if yes, redirect
#     if 'username' in session:
#         flash("You're already logged in.", 'warning')
#         return redirect('/users/' + session['username'])

#     form = RegisterForm()

#     # Check if the form has been submitted and is valid
#     if form.validate_on_submit():
#         # Extract form data
#         username = form.username.data
#         password = form.password.data
#         email = form.email.data
#         first_name = form.first_name.data
#         last_name = form.last_name.data

#         # Check if a username or email already exists in the database
#         if not check_user_existence(username, email):
#             # Register and log in the user
#             register_user(username, password, email, first_name, last_name)
#             flash('Your registration was successful.', 'success')
#             return redirect('/users/' + session['username'])
#     else:        
#         # Flash any form validation errors
#         flash_form_errors(form)
#     return render_template('/registration_form.html', form=form)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """Handles user login"""
#     # Check if the user is already logged in, if yes, redirect
#     if 'username' in session:
#         flash("You're already logged in.", 'warning')
#         return redirect('/users/' + session['username'])

#     form = LoginForm()

#     # Check if the form has been submitted and is valid
#     if form.validate_on_submit():
#         # Extract form data
#         username = form.username.data
#         password = form.password.data

#         # Authenticate the user
#         user = User.authenticate(username, password)

#         if user:
#             # Set the session username and redirect to the user's page
#             session['username'] = user.username
#             return redirect('/users/' + session['username'])
#         else:
#             # Display an error message if the username or password is invalid
#             flash('Invalid username or password', 'danger')
#             return redirect('/login')

#     return render_template('login_form.html', form=form)


# @app.route('/logout', methods=['POST'])
# def logout():
#     """Handles user logout"""
#     if 'username' in session:
#         # Clear the user's session information
#         session.pop('username')  
#     return redirect('/')


# @app.route('/logout')
# def logout_url():
#     """Handle logout URL access"""
#     if 'username' in session:
#         # User is logged in, display a message for logged-in users
#         flash('Please use the Logout button to log out.', 'warning')
#         return redirect('/users/' + session['username'])
#     else:
#         # User is not logged in, display a message for not logged-in users
#         flash('You are not logged in. Please log in if you have an account.', 'danger')
#         return redirect('/')


# @app.route('/users/<username>')
# def user_details(username):
#     """Handles user details display"""
#     # Check if the requested username matches the session username
#     if username == session['username']:
#         user = User.query.filter_by(username=username).first()
#         if user:
#             # Get stored flash message from session (return value if any else none then remove)
#             flash_msg = session.pop('flash_msg', None) 
#             if flash_msg is not None:
#                 flash(flash_msg, 'success')
#             # Render the user details template for the logged-in user
#             return render_template('user_details.html', user=user)
#         else:
#             # Display an error message if the user is not found
#             flash('User not found', 'danger')
#             return redirect('/')
#     else:
#         # Display a message indicating that the user can only view their own details
#         flash('You can only view your own user details.', 'danger')
#         return redirect('/users/' + session['username'])

# @app.route('/users/<username>/delete')
# def delete_user(username):
#     """Handles user deletion"""
#     # Check if the requested username matches the session username
#     if username == session['username']:
#         user = User.query.filter_by(username=username).first()
#         if user:
#             # Get all associated feedbacks
#             feedbacks = Feedback.query.filter_by(user_username=username).all()

#             # Delete each feedback item
#             for feedback in feedbacks:
#                 db.session.delete(feedback)

#             # Delete the user
#             db.session.delete(user)
#             db.session.commit()
            
#             session.pop('username') 
#             flash('User and associated feedbacks deleted successfully.', 'success')
#             return redirect('/')
#         else:
#             # Display an error message if the user is not found
#             flash('User not found', 'danger')
#             return redirect('/')
#     else:
#         # Display a message indicating that the user can only delete their own account
#         flash('You can only delete your own account.', 'danger')
#         return redirect('/users/' + session['username'])


# @app.route('/feedbacks', methods=['GET', 'POST'])
# def feedback():
#     """Handles adding new feedbacks form"""
#     form = FeedbackForm()

#     if form.validate_on_submit():
#         title = form.title.data
#         content = form.content.data

#         # Retrieve the user associated with the session username
#         user = User.query.filter_by(username=session['username']).first()

#         if user:
#             # Create a new feedback associated with the user
#             new_feedback = Feedback(title=title, content=content, user=user)
#             db.session.add(new_feedback)
#             db.session.commit()
            
#             # Display a success message and redirect to the user's page
#             flash('Feedback successfully submitted.', 'success')
#             return redirect('/users/' + session['username'])
#         else:
#             # Display an error message if the user is not found
#             flash('User not found.', 'danger')
#     else:
#         # Flash any form validation errors
#         flash_form_errors(form)        
#         return render_template('feedback.html', form=form)


# @app.route('/feedbacks/<int:id>')
# def feedback_details(id):
#     """Handles feedback details display"""
#     # Retrieve the feedback item with the specified ID
#     feedback = Feedback.query.get_or_404(id)
#     # Check if the feedback belongs to the logged-in user
#     if feedback.user_username == session['username']:
#         return render_template('feedback_details.html', feedback=feedback)
#     else:
#         flash('You can only edit your own feedbacks.', 'danger')
#         return redirect('/users/' + session['username'])


# @app.route('/feedbacks/<int:id>', methods=['DELETE'])
# def handle_feedback_deletion(id):
#     """Handles feedback deletion"""
#     # Retrieve the feedback item with the specified ID
#     feedback = Feedback.query.get_or_404(id)
#     # Check if the feedback belongs to the logged-in user
#     if feedback.user_username == session['username']:
#         db.session.delete(feedback)
#         db.session.commit()
#         # Store message in session to retrieve in different app route (page)
#         session['flash_msg'] = 'Feedback deleted successfully' 
#         return jsonify(message='deleted')  
#     else:
#         return jsonify(message='Feedback not found'), 404


# @app.route('/feedbacks/<int:id>', methods=['PATCH'])
# def handle_feedback_update(id):
#     """Handles feedback update"""
#     # Retrieve the feedback item with the specified ID
#     feedback = Feedback.query.get_or_404(id)
#     # Check if the feedback belongs to the logged-in user
#     if feedback.user_username == session['username']:
#         feedback.title = request.json.get('title', feedback.title)
#         feedback.content = request.json.get('content', feedback.content)
#         db.session.commit()
#         # Store message in session to retrieve in different app route (page)
#         session['flash_msg'] = 'Feedback updated successfully' 
#         return jsonify(message='Updated')
#     else:
#         return jsonify(message='Feedback not found'), 404





# # Function to check if a username or email already exists in the database
# def check_user_existence(username, email):
#     username_exists = User.query.filter_by(username=username).first()
#     email_exists = User.query.filter_by(email=email).first()

#     if username_exists:
#         flash('Username already exists.', 'danger')
#         return True
#     elif email_exists:
#         flash('Email already exists.', 'danger')
#         return True
#     return False

# # Function to register a new user
# def register_user(username, password, email, first_name, last_name):
#     registered_user = User.register(username, password)
#     new_user = User(
#         username=username,
#         password=registered_user.password,
#         email=email,
#         first_name=first_name,
#         last_name=last_name,
#     )
#     db.session.add(new_user)
#     db.session.commit()
#     session['username'] = new_user.username

# # Function to flash error messages for form validation failures
# def flash_form_errors(form):
#     for field, errors in form.errors.items():
#         for error in errors:
#             flash(f'{field.capitalize()}: {error}', 'danger')
 














# @app.route('/')
# def list_cupcakes():
#     return render_template('cupcake_list.html')

# @app.route('/api/cupcakes')  # GET all
# def get_all_cupcakes():
#     all_cupcakes = [cupcake.serialize() for cupcake in Cupcake.query.all()]
#     return jsonify(cupcake=all_cupcakes)  

# @app.route('/api/cupcakes/<int:id>')  # GET single
# def get_a_cupcake(id):
#     cupcake = Cupcake.query.get_or_404(id)
#     return jsonify(cupcake=cupcake.serialize())  


# @app.route('/api/cupcakes', methods=['POST'])   # POST to create (code 201)
# def create_cupcake():
#     new_cupcake = Cupcake(
#         flavor=request.json['flavor'],
#         size=request.json['size'],
#         rating=request.json['rating'],
#         image=request.json['image']
#     )
#     db.session.add(new_cupcake)
#     db.session.commit()
#     return (jsonify(cupcake=new_cupcake.serialize()), 201) 

# @app.route('/api/cupcakes/<int:id>', methods=['PATCH'])  # PATCH (partial update)
# def update_cupcake(id):
#     cupcake = Cupcake.query.get_or_404(id)

#     cupcake.flavor = request.json.get('flavor',cupcake.flavor)    
#     cupcake.size = request.json.get('size',cupcake.size)
#     cupcake.rating = request.json.get('rating',cupcake.rating)
#     cupcake.image = request.json.get('image',cupcake.image)
   
#     db.session.commit()
#     return jsonify(cupcake=cupcake.serialize())  

# @app.route('/api/cupcakes/<int:id>', methods=['DELETE'])
# def delete_cupcake(id):
#     cupcake = Cupcake.query.get_or_404(id)
#     db.session.delete(cupcake)
#     db.session.commit()
#     return jsonify(message='deleted')  


