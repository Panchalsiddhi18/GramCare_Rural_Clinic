from app import app
from models import db
from models.user import User, Patient
from models.clinic import Clinic, Doctor
from models.appointment import Appointment
from models.notification import Notification
from datetime import date, datetime

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # 1. Clinics
        c1 = Clinic(name="GramCare Primary Health Centre", district="Palanpur", taluka="Banaskantha", address="Main Highway Road, Village Centre", avg_consultation_time=8)
        c2 = Clinic(name="Community Health Centre - Deesa", district="Palanpur", taluka="Deesa", address="Near Bus Station", avg_consultation_time=10)
        db.session.add_all([c1, c2])
        db.session.commit()

        # 2. Staff User
        u_staff = User(email="staff@demo.com", role="staff", full_name="Ramesh Patel (Staff)", phone="9876543210")
        u_staff.set_password("demo123")
        db.session.add(u_staff)

        # 3. Doctor User & Profile
        u_doc = User(email="doctor@demo.com", role="doctor", full_name="Dr. Anil Sharma", phone="9876543211")
        u_doc.set_password("demo123")
        db.session.add(u_doc)
        db.session.flush()

        doc1 = Doctor(user_id=u_doc.id, clinic_id=c1.id, specialization="General Physician", room_number="Room #2")
        db.session.add(doc1)

        # 4. Patient User & Profile
        u_pat = User(email="patient@demo.com", role="patient", full_name="Sita Devi", phone="9876543212")
        u_pat.set_password("demo123")
        db.session.add(u_pat)
        db.session.flush()

        pat1 = Patient(user_id=u_pat.id, age=62, gender="Female", village="Gadh Village", abha_id="ABHA-1029-3847")
        db.session.add(pat1)
        db.session.commit()

        # 5. Additional Demo Patients for Queue Depth
        demo_names = ["Kishan Kumar", "Radha Ben", "Mohan Lal", "Vikram Singh"]
        today = date.today()

        # Create active appointments
        a1 = Appointment(patient_id=pat1.id, doctor_id=doc1.id, clinic_id=c1.id, appointment_date=today, time_slot="09:00 AM", status="NOW SERVING", priority="ELDERLY", token_number=101)
        db.session.add(a1)

        for idx, name in enumerate(demo_names, start=102):
            u = User(email=f"patient_{idx}@demo.com", role="patient", full_name=name)
            u.set_password("demo123")
            db.session.add(u)
            db.session.flush()

            p = Patient(user_id=u.id, age=30 + idx % 20, gender="Male" if idx % 2 == 0 else "Female", village="Nearby Village")
            db.session.add(p)
            db.session.flush()

            priority_type = "PREGNANT" if idx == 103 else ("URGENT" if idx == 104 else "NORMAL")
            appt = Appointment(patient_id=p.id, doctor_id=doc1.id, clinic_id=c1.id, appointment_date=today, time_slot="09:30 AM", status="WAITING", priority=priority_type, token_number=idx)
            db.session.add(appt)

        db.session.commit()
        print("Demo database populated successfully with realistic queue data.")

if __name__ == '__main__':
    seed_database()

