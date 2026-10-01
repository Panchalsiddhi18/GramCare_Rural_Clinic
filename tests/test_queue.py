import pytest
from app import app
from models import db
from models.clinic import Clinic, Doctor
from models.appointment import Appointment
from datetime import date

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_priority_queue_sorting(client):
    with app.app_context():
        c = Clinic(name="Test Clinic", district="Test", taluka="Test", address="Test", avg_consultation_time=10)
        db.session.add(c)
        db.session.commit()

        # Token 1 (Normal) vs Token 2 (Urgent)
        a1 = Appointment(patient_id=1, doctor_id=1, clinic_id=c.id, appointment_date=date.today(), time_slot="09:00", token_number=1, priority="NORMAL")
        a2 = Appointment(patient_id=2, doctor_id=1, clinic_id=c.id, appointment_date=date.today(), time_slot="09:00", token_number=2, priority="URGENT")

        db.session.add_all([a1, a2])
        db.session.commit()

        queue = [a1, a2]
        queue.sort(key=lambda x: x.calculate_effective_priority())

        # Verify urgent case (Token 2) moved ahead of Token 1
        assert queue[0].token_number == 2
