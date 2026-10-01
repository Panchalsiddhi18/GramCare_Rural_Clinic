from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.appointment import Appointment
from datetime import date, datetime

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('index'))

    doctor = current_user.doctor_profile
    today = date.today()

    serving = Appointment.query.filter_by(doctor_id=doctor.id, appointment_date=today, status='NOW SERVING').first()

    waiting = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == today,
        Appointment.status.in_(['CHECKED-IN', 'WAITING'])
    ).all()
    waiting.sort(key=lambda a: a.calculate_effective_priority())

    completed_today = Appointment.query.filter_by(doctor_id=doctor.id, appointment_date=today, status='COMPLETED').all()

    return render_template('doctor_dashboard.html', 
                           serving=serving, 
                           waiting=waiting, 
                           completed_count=len(completed_today),
                           doctor=doctor)

@doctor_bp.route('/complete/<int:id>', methods=['POST'])
@login_required
def complete(id):
    appt = Appointment.query.get_or_404(id)
    appt.status = 'COMPLETED'
    appt.completed_at = datetime.utcnow()
    db.session.commit()
    flash(f'Consultation for Token #{appt.token_number} marked as COMPLETED.', 'success')
    return redirect(url_for('doctor.dashboard'))

