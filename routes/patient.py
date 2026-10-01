from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.clinic import Clinic, Doctor
from models.appointment import Appointment
from models.notification import Notification
from datetime import date, datetime

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'patient':
        return redirect(url_for('index'))

    patient = current_user.patient_profile
    today = date.today()

    active_appointment = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date == today,
        Appointment.status.in_(['BOOKED', 'CHECKED-IN', 'WAITING', 'NOW SERVING'])
    ).first()

    queue_info = None
    if active_appointment and active_appointment.status in ['WAITING', 'NOW SERVING']:
        clinic = active_appointment.clinic
        doctor = active_appointment.doctor

        # Get current serving token
        serving = Appointment.query.filter_by(
            doctor_id=doctor.id,
            appointment_date=today,
            status='NOW SERVING'
        ).first()

        current_token = serving.token_number if serving else 0

        # Calculate position ahead using effective priority ordering
        waiting_list = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today,
            Appointment.status.in_(['CHECKED-IN', 'WAITING'])
        ).all()

        waiting_list.sort(key=lambda a: a.calculate_effective_priority())
        
        patients_ahead = 0
        for idx, appt in enumerate(waiting_list):
            if appt.id == active_appointment.id:
                patients_ahead = idx
                break

        est_wait = patients_ahead * clinic.avg_consultation_time

        queue_info = {
            'current_token': current_token,
            'your_token': active_appointment.token_number,
            'patients_ahead': patients_ahead,
            'est_wait': est_wait,
            'priority': active_appointment.priority,
            'doctor_name': doctor.user.full_name,
            'clinic_name': clinic.name,
            'status': active_appointment.status
        }

    history = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.created_at.desc()).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()

    return render_template('patient_dashboard.html', 
                           active=active_appointment, 
                           queue_info=queue_info, 
                           history=history,
                           notifications=notifications)

@patient_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id', type=int)
        clinic_id = request.form.get('clinic_id', type=int)
        time_slot = request.form.get('time_slot', '09:00 AM - 10:00 AM')

        patient = current_user.patient_profile
        today = date.today()

        # Check existing booking for today
        existing = Appointment.query.filter_by(patient_id=patient.id, appointment_date=today).filter(
            Appointment.status.notin_(['CANCELLED', 'COMPLETED'])
        ).first()

        if existing:
            flash('You already have an active appointment scheduled for today.', 'warning')
            return redirect(url_for('patient.dashboard'))

        # Generate next sequential token for the doctor today
        max_token = db.session.query(db.func.max(Appointment.token_number)).filter_by(
            doctor_id=doctor_id, appointment_date=today
        ).scalar() or 0

        next_token = max_token + 1

        new_appt = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            clinic_id=clinic_id,
            appointment_date=today,
            time_slot=time_slot,
            status='BOOKED',
            token_number=next_token,
            priority='NORMAL'
        )
        db.session.add(new_appt)
        db.session.commit()

        # Generate Confirmation Notification
        notif = Notification(
            user_id=current_user.id,
            message=f"Appointment confirmed at {new_appt.clinic.name}. Your Token Number is #{next_token}.",
            category="BOOKING"
        )
        db.session.add(notif)
        db.session.commit()

        flash(f'Appointment booked successfully! Your Token is #{next_token}', 'success')
        return redirect(url_for('patient.dashboard'))

    clinics = Clinic.query.all()
    doctors = Doctor.query.all()
    return render_template('booking.html', clinics=clinics, doctors=doctors)

@patient_bp.route('/cancel/<int:id>', methods=['POST'])
@login_required
def cancel(id):
    appt = Appointment.query.get_or_404(id)
    if appt.patient.user_id == current_user.id and appt.status in ['BOOKED', 'CHECKED-IN', 'WAITING']:
        appt.status = 'CANCELLED'
        db.session.commit()
        flash('Appointment cancelled.', 'info')
    return redirect(url_for('patient.dashboard'))

