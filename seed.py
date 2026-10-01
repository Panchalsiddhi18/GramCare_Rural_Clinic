from app import app
from models import db

from models.user import User, Patient
from models.clinic import Clinic, Doctor
from models.appointment import Appointment
from models.notification import Notification

from datetime import date


def seed_database():

    with app.app_context():

        # -------------------------------------------------
        # RESET DATABASE
        # -------------------------------------------------

        db.drop_all()
        db.create_all()


        # =================================================
        # 1. CLINICS
        # =================================================

        clinic_1 = Clinic(
            name="GramCare Primary Health Centre",
            district="Palanpur",
            taluka="Banaskantha",
            address="Main Highway Road, Village Centre",
            avg_consultation_time=8
        )

        clinic_2 = Clinic(
            name="Community Health Centre - Deesa",
            district="Palanpur",
            taluka="Deesa",
            address="Near Bus Station",
            avg_consultation_time=10
        )

        db.session.add_all([
            clinic_1,
            clinic_2
        ])

        db.session.commit()


        # =================================================
        # 2. STAFF
        # =================================================

        staff_user = User(
            email="staff@demo.com",
            role="staff",
            full_name="Ramesh Patel",
            phone="9876543210"
        )

        staff_user.set_password("demo123")

        db.session.add(staff_user)


        # =================================================
        # 3. DOCTORS
        # =================================================

        doctors_data = [

            {
                "email": "doctor.anil@demo.com",
                "name": "Dr. Anil Sharma",
                "phone": "9876543211",
                "clinic": clinic_1,
                "specialization": "General Physician",
                "room": "Room #2"
            },

            {
                "email": "doctor.meera@demo.com",
                "name": "Dr. Meera Joshi",
                "phone": "9876543213",
                "clinic": clinic_1,
                "specialization": "Pediatrician",
                "room": "Room #3"
            },

            {
                "email": "doctor.kavita@demo.com",
                "name": "Dr. Kavita Patel",
                "phone": "9876543214",
                "clinic": clinic_1,
                "specialization": "Gynecologist",
                "room": "Room #4"
            },

            {
                "email": "doctor.rajiv@demo.com",
                "name": "Dr. Rajiv Shah",
                "phone": "9876543215",
                "clinic": clinic_2,
                "specialization": "Orthopedic",
                "room": "Room #1"
            },

            {
                "email": "doctor.neha@demo.com",
                "name": "Dr. Neha Desai",
                "phone": "9876543216",
                "clinic": clinic_2,
                "specialization": "Dermatologist",
                "room": "Room #2"
            }

        ]


        doctor_profiles = []


        for data in doctors_data:

            user = User(
                email=data["email"],
                role="doctor",
                full_name=data["name"],
                phone=data["phone"]
            )

            user.set_password("demo123")

            db.session.add(user)

            db.session.flush()


            doctor = Doctor(
                user_id=user.id,
                clinic_id=data["clinic"].id,
                specialization=data["specialization"],
                room_number=data["room"],
                is_available=True
            )

            db.session.add(doctor)

            doctor_profiles.append(
                doctor
            )


        db.session.commit()


        # =================================================
        # 4. DEMO PATIENT
        # =================================================

        patient_user = User(
            email="patient@demo.com",
            role="patient",
            full_name="Sita Devi",
            phone="9876543212"
        )

        patient_user.set_password("demo123")

        db.session.add(patient_user)

        db.session.flush()


        patient = Patient(
            user_id=patient_user.id,
            age=62,
            gender="Female",
            village="Gadh Village",
            abha_id="ABHA-1029-3847"
        )

        db.session.add(patient)

        db.session.commit()


        # =================================================
        # 5. DEMO QUEUE
        # =================================================

        general_doctor = doctor_profiles[0]

        today = date.today()


        # Current patient
        current_appointment = Appointment(
            patient_id=patient.id,
            doctor_id=general_doctor.id,
            clinic_id=clinic_1.id,
            appointment_date=today,
            time_slot="09:00 AM",
            status="NOW SERVING",
            priority="ELDERLY",
            token_number=101
        )

        db.session.add(
            current_appointment
        )


        # -------------------------------------------------
        # Additional queue patients
        # -------------------------------------------------

        demo_patients = [

            {
                "name": "Kishan Kumar",
                "email": "patient_102@demo.com",
                "age": 34,
                "gender": "Male",
                "priority": "NORMAL",
                "token": 102
            },

            {
                "name": "Radha Ben",
                "email": "patient_103@demo.com",
                "age": 29,
                "gender": "Female",
                "priority": "PREGNANT",
                "token": 103
            },

            {
                "name": "Mohan Lal",
                "email": "patient_104@demo.com",
                "age": 45,
                "gender": "Male",
                "priority": "URGENT",
                "token": 104
            },

            {
                "name": "Vikram Singh",
                "email": "patient_105@demo.com",
                "age": 41,
                "gender": "Male",
                "priority": "NORMAL",
                "token": 105
            }

        ]


        for data in demo_patients:

            user = User(
                email=data["email"],
                role="patient",
                full_name=data["name"]
            )

            user.set_password("demo123")

            db.session.add(user)

            db.session.flush()


            demo_patient = Patient(
                user_id=user.id,
                age=data["age"],
                gender=data["gender"],
                village="Nearby Village"
            )

            db.session.add(
                demo_patient
            )

            db.session.flush()


            appointment = Appointment(
                patient_id=demo_patient.id,
                doctor_id=general_doctor.id,
                clinic_id=clinic_1.id,
                appointment_date=today,
                time_slot="09:30 AM",
                status="WAITING",
                priority=data["priority"],
                token_number=data["token"]
            )

            db.session.add(
                appointment
            )


        # =================================================
        # 6. DEMO NOTIFICATION
        # =================================================

        notification = Notification(
            user_id=patient_user.id,
            message=(
                "Welcome to GramCare. "
                "You can now choose a clinic, "
                "department and doctor for your appointment."
            ),
            category="SYSTEM"
        )

        db.session.add(
            notification
        )


        # =================================================
        # SAVE EVERYTHING
        # =================================================

        db.session.commit()


        print("")
        print("=" * 60)
        print("GRAMCARE DEMO DATABASE CREATED")
        print("=" * 60)

        print("")
        print("CLINICS")
        print("1. GramCare Primary Health Centre")
        print("2. Community Health Centre - Deesa")

        print("")
        print("DOCTORS")

        for doctor in doctor_profiles:

            print(
                f"- {doctor.user.full_name} | "
                f"{doctor.specialization} | "
                f"{doctor.clinic.name}"
            )

        print("")
        print("PATIENT LOGIN")
        print("Email: patient@demo.com")
        print("Password: demo123")

        print("")
        print("DOCTOR LOGINS")

        for data in doctors_data:

            print(
                f"{data['email']} / demo123"
            )

        print("")
        print("Database seeded successfully.")
        print("=" * 60)


if __name__ == "__main__":
    seed_database()