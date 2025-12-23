from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os

app = Flask(__name__)
CORS(app)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fitness.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    age = db.Column(db.Integer)
    height_cm = db.Column(db.Integer)
    weight_kg = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    workouts = db.relationship('Workout', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'created_at': self.created_at.isoformat()
        }

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_type = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer)
    date = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    exercises = db.relationship('Exercise', backref='workout', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'workout_type': self.workout_type,
            'duration_minutes': self.duration_minutes,
            'calories_burned': self.calories_burned,
            'date': self.date.isoformat() if self.date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'exercises': [e.to_dict() for e in self.exercises]
        }

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight_kg = db.Column(db.Float)
    duration_minutes = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sets': self.sets,
            'reps': self.reps,
            'weight_kg': self.weight_kg,
            'duration_minutes': self.duration_minutes
        }

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"error": "Username already exists"}), 400
    
    user = User(
        username=data.get('username'),
        email=data.get('email'),
        age=data.get('age'),
        height_cm=data.get('height_cm'),
        weight_kg=data.get('weight_kg')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    user_id = request.args.get('user_id')
    workouts = Workout.query.order_by(Workout.date.desc(), Workout.created_at.desc()).all()
    if user_id:
        workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.date.desc(), Workout.created_at.desc()).all()
    return jsonify([w.to_dict() for w in workouts])

@app.route('/api/workouts', methods=['POST'])
def create_workout():
    data = request.json
    workout = Workout(
        user_id=data.get('user_id'),
        workout_type=data.get('workout_type'),
        duration_minutes=data.get('duration_minutes'),
        calories_burned=data.get('calories_burned'),
        date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else date.today(),
        notes=data.get('notes', '')
    )
    db.session.add(workout)
    db.session.flush()
    
    # Add exercises if provided
    exercises_data = data.get('exercises', [])
    for ex_data in exercises_data:
        exercise = Exercise(
            workout_id=workout.id,
            name=ex_data.get('name'),
            sets=ex_data.get('sets'),
            reps=ex_data.get('reps'),
            weight_kg=ex_data.get('weight_kg'),
            duration_minutes=ex_data.get('duration_minutes')
        )
        db.session.add(exercise)
    
    db.session.commit()
    return jsonify(workout.to_dict()), 201

@app.route('/api/workouts/<int:workout_id>', methods=['GET'])
def get_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    return jsonify(workout.to_dict())

@app.route('/api/workouts/<int:workout_id>/stats', methods=['GET'])
def get_workout_stats():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    workouts = Workout.query.filter_by(user_id=user_id).all()
    total_workouts = len(workouts)
    total_calories = sum(w.calories_burned or 0 for w in workouts)
    total_minutes = sum(w.duration_minutes for w in workouts)
    
    return jsonify({
        'total_workouts': total_workouts,
        'total_calories_burned': total_calories,
        'total_minutes': total_minutes
    })

if __name__ == '__main__':
    app.run(debug=True, port=5006)

