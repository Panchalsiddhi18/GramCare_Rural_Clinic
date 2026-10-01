from models import db
from datetime import datetime, date

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    
    appointment_date = db.Column(db.Date, nullable=False, default=date.today)
    time_slot = db.Column(db.String(20), nullable=False)
    
    # BOOKED, CHECKED-IN, WAITING, NOW SERVING, COMPLETED, CANCELLED, NO-SHOW
    status = db.Column(db.String(30), default='BOOKED', nullable=False)
    priority = db.Column(db.String(20), default='NORMAL', nullable=False) # NORMAL, ELDERLY, PREGNANT, DISABILITY, URGENT
    
    token_number = db.Column(db.Integer, nullable=True)
    token_sequence = db.Column(db.Float, nullable=True)  # Used for priority sorting
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    checked_in_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    def calculate_effective_priority(self):
        # Operational sorting weight: lower number moves ahead in queue safely
        weights = {
            'URGENT': 0.1,
            'PREGNANT': 0.4,
            'DISABILITY': 0.5,
            'ELDERLY': 0.6,
            'NORMAL': 1.0
        }
        base = self.token_number if self.token_number else 999
        return base * weights.get(self.priority, 1.0)

