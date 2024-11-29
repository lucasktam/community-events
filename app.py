from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

# Initialize Flask app and configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

# Initialize SQLAlchemy and Flask-Login
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(500))
    location = db.Column(db.JSON)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    author_username = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)
    author = db.relationship('User', backref=db.backref('events', lazy=True))

# Initialize user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route to display the home page and handle login/logout
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if any users exist
        if User.query.count() == 0:
            # If no users, create the first user with the submitted credentials
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect('/')


        user = User.query.filter_by(username=username).first()

        if not user:
            # If no user with this username exists, create a new user
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect('/')
        
        if user and user.password == password:  # Check if credentials match
            login_user(user)
            return redirect('/')
        return render_template('index.html', inv_msg=True)
    
    return render_template('index.html', inv_msg=False)

# Route to log out
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
