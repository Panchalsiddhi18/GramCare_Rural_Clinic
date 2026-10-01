from models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient', 'staff', 'doctor'
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade="all, delete-orphan")
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    # Basic information
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    village = db.Column(db.String(100), nullable=True)
    abha_id = db.Column(db.String(50), nullable=True)

    # Health profile
    blood_group = db.Column(
        db.String(10),
        nullable=True
    )

    emergency_contact = db.Column(
        db.String(20),
        nullable=True
    )

    allergies = db.Column(
        db.Text,
        nullable=True
    )

    medical_history = db.Column(
        db.Text,
        nullable=True
    )

    current_medications = db.Column(
        db.Text,
        nullable=True
    )

    appointments = db.relationship(
        'Appointment',
        backref='patient',
        lazy=True
    )