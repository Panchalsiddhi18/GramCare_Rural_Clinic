from models import db

class Clinic(db.Model):
    __tablename__ = 'clinics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    district = db.Column(db.String(80), nullable=False)
    taluka = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    avg_consultation_time = db.Column(db.Integer, default=10)  # in minutes

    doctors = db.relationship('Doctor', backref='clinic', lazy=True)
    appointments = db.relationship('Appointment', backref='clinic', lazy=True)


class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    specialization = db.Column(db.String(80), default="General Physician")
    room_number = db.Column(db.String(20), default="OPD Room 1")
    is_available = db.Column(db.Boolean, default=True)

    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

