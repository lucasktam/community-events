from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta

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
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=datetime.utcnow)
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
        if 'Login' in request.form:
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
            
            events = Event.query.all()
            return render_template('index.html', inv_msg=True, events=events)
        

        elif 'Add Event' in request.form:
            event_title = request.form.get('title')
            event_content = request.form.get('content')

            event_time_str = request.form.get('year') + '-' + request.form.get('month') + '-' + request.form.get('day') + ' ' + request.form.get('time') + ':00'
            event_time = datetime.strptime(event_time_str, '%Y-%m-%d %H:%M:%S')

            event_time_end_str = request.form.get('duration')

            # Allowed formats: HH:mm or mm
            full_format = False
            i = 0
            if event_time_end_str[0] == ':':
                events = Event.query.all() 
                return render_template('index.html', wrong_format=True, events=events)
            while i < len(event_time_end_str) and event_time_end_str[i] != ':' :
                if (event_time_end_str[i] < '0' or event_time_end_str[i] > '9'):
                    events = Event.query.all() 
                    return render_template('index.html', wrong_format=True, events=events)
                i += 1
            if event_time_end_str[i] == ':' and i == len(event_time_end_str) - 1:
                events = Event.query.all() 
                return render_template('index.html', wrong_format=True, events=events)
            i += 1
            
            while i < len(event_time_end_str):
                if (event_time_end_str[i] < '0' or event_time_end_str[i] > '9'):
                    events = Event.query.all() 
                    return render_template('index.html', wrong_format=True, events=events)
                full_format = True
                i += 1



            new_event = Event(
                title=event_title, 
                content=event_content, 
                start_date=event_time,
                author_username=current_user.username
            )
            
            if (full_format):
                h, m = map(int, event_time_end_str.split(":"))
                new_event.end_date = new_event.start_date + timedelta(hours = h, minutes = m)
            else:
                h = 0
                m = int(event_time_end_str)
                new_event.end_date = new_event.start_date + timedelta(hours = h, minutes = m)

            try:
                db.session.add(new_event)
                db.session.commit()
                return redirect('/')
            except:
                return 'issue adding task'
            
    else:  # If the request is a GET (user loads the page)
        events = Event.query.all() 
        return render_template('index.html', events=events)

        
    return render_template('index.html', inv_msg=False)

@app.route('/delete/<int:id>')
def delete(id):
    event_to_delete = Event.query.get_or_404(id)

    try:
        db.session.delete(event_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'there was a problem deleting'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    event = Event.query.get_or_404(id)
    if request.method == 'POST':
        event.content = request.form['content']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'there was a problem updating'
    else:
        return render_template('update.html', event=event)

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
