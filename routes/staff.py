from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.appointment import Appointment
from models.clinic import Clinic, Doctor
from models.notification import Notification
from datetime import date, datetime

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'staff':
        return redirect(url_for('index'))

    today = date.today()
    # Assume staff works at Clinic 1 for MVP demo
    clinic = Clinic.query.first()
    
    appointments = Appointment.query.filter_by(clinic_id=clinic.id, appointment_date=today).all()
    
    # Sort waiting queue by priority rules
    waiting_queue = [a for a in appointments if a.status in ['CHECKED-IN', 'WAITING']]
    waiting_queue.sort(key=lambda a: a.calculate_effective_priority())

    serving = Appointment.query.filter_by(clinic_id=clinic.id, appointment_date=today, status='NOW SERVING').first()

    stats = {
        'total': len(appointments),
        'waiting': len(waiting_queue),
        'completed': len([a for a in appointments if a.status == 'COMPLETED']),
        'noshow': len([a for a in appointments if a.status == 'NO-SHOW']),
        'current_token': serving.token_number if serving else '-'
    }

    doctors = Doctor.query.filter_by(clinic_id=clinic.id).all()

    return render_template('staff_dashboard.html', 
                           appointments=appointments, 
                           waiting_queue=waiting_queue, 
                           serving=serving, 
                           stats=stats,
                           clinic=clinic,
                           doctors=doctors)

@staff_bp.route('/checkin/<int:id>', methods=['POST'])
@login_required
def checkin(id):
    appt = Appointment.query.get_or_404(id)
    appt.status = 'WAITING'
    appt.checked_in_at = datetime.utcnow()
    db.session.commit()
    flash(f'Token #{appt.token_number} checked in and added to active queue.', 'success')
    return redirect(url_for('staff.dashboard'))

@staff_bp.route('/update_priority/<int:id>', methods=['POST'])
@login_required
def update_priority(id):
    appt = Appointment.query.get_or_404(id)
    new_priority = request.form.get('priority', 'NORMAL')
    appt.priority = new_priority
    db.session.commit()

    # Notify patient of priority adjustment
    notif = Notification(
        user_id=appt.patient.user_id,
        message=f"Queue priority updated to '{new_priority}'. Position re-indexed.",
        category="PRIORITY"
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Token #{appt.token_number} priority updated to {new_priority}.', 'info')
    return redirect(url_for('staff.dashboard'))

@staff_bp.route('/call_next', methods=['POST'])
@login_required
def call_next():
    doctor_id = request.form.get('doctor_id', type=int)
    today = date.today()

    # Complete current serving if exists
    current = Appointment.query.filter_by(doctor_id=doctor_id, appointment_date=today, status='NOW SERVING').first()
    if current:
        current.status = 'COMPLETED'
        current.completed_at = datetime.utcnow()

    # Get next patient by weighted priority
    waiting = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == today,
        Appointment.status.in_(['CHECKED-IN', 'WAITING'])
    ).all()

    if waiting:
        waiting.sort(key=lambda a: a.calculate_effective_priority())
        next_patient = waiting[0]
        next_patient.status = 'NOW SERVING'
        db.session.commit()

        # Send Turn-Approaching and Call Notifications
        notif = Notification(
            user_id=next_patient.patient.user_id,
            message=f"Token #{next_patient.token_number}: It is your turn! Please proceed to {next_patient.doctor.room_number}.",
            category="CALL"
        )
        db.session.add(notif)
        
        # Check second next patient and alert them
        if len(waiting) > 1:
            second_next = waiting[1]
            notif_near = Notification(
                user_id=second_next.patient.user_id,
                message=f"Token #{second_next.token_number}: Your turn is approaching. Only 1 patient ahead.",
                category="APPROACHING"
            )
            db.session.add(notif_near)

        db.session.commit()
        flash(f'Called Token #{next_patient.token_number} to {next_patient.doctor.room_number}.', 'success')
    else:
        db.session.commit()
        flash('No patients waiting in queue.', 'warning')

    return redirect(url_for('staff.dashboard'))

