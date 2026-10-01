from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from models import db
from models.appointment import Appointment

from datetime import date, datetime


doctor_bp = Blueprint(
    'doctor',
    __name__,
    url_prefix='/doctor'
)


# =========================================================
# DOCTOR DASHBOARD
# =========================================================

@doctor_bp.route('/dashboard')
@login_required
def dashboard():

    if current_user.role != 'doctor':
        return redirect(url_for('index'))

    doctor = current_user.doctor_profile

    if not doctor:

        flash(
            'Doctor profile was not found.',
            'danger'
        )

        return redirect(
            url_for('auth.login')
        )

    today = date.today()


    # -----------------------------------------------------
    # CURRENTLY SERVING
    # -----------------------------------------------------

    serving = (
        Appointment.query
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today,
            Appointment.status == 'NOW SERVING'
        )
        .order_by(
            Appointment.token_number.asc()
        )
        .first()
    )


    # -----------------------------------------------------
    # WAITING QUEUE
    # -----------------------------------------------------

    waiting = (
        Appointment.query
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today,
            Appointment.status.in_([
                'BOOKED',
                'CHECKED-IN',
                'WAITING'
            ])
        )
        .all()
    )


    waiting.sort(
        key=lambda appointment:
        appointment.calculate_effective_priority()
    )


    # -----------------------------------------------------
    # COMPLETED TODAY
    # -----------------------------------------------------

    completed_today = (
        Appointment.query
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today,
            Appointment.status == 'COMPLETED'
        )
        .all()
    )


    return render_template(
        'doctor_dashboard.html',
        serving=serving,
        waiting=waiting,
        completed_count=len(completed_today),
        doctor=doctor
    )


# =========================================================
# START SERVING
# =========================================================

@doctor_bp.route(
    '/start/<int:id>',
    methods=['POST']
)
@login_required
def start_serving(id):

    if current_user.role != 'doctor':
        return redirect(url_for('index'))


    doctor = current_user.doctor_profile

    if not doctor:

        flash(
            'Doctor profile was not found.',
            'danger'
        )

        return redirect(
            url_for('auth.login')
        )


    appointment = Appointment.query.get_or_404(id)


    # -----------------------------------------------------
    # SECURITY CHECK
    # -----------------------------------------------------

    if appointment.doctor_id != doctor.id:

        flash(
            'You are not authorized to manage this appointment.',
            'danger'
        )

        return redirect(
            url_for('doctor.dashboard')
        )


    # -----------------------------------------------------
    # ONLY TODAY'S APPOINTMENT
    # -----------------------------------------------------

    if appointment.appointment_date != date.today():

        flash(
            'Only today\'s appointments can be started.',
            'warning'
        )

        return redirect(
            url_for('doctor.dashboard')
        )


    # -----------------------------------------------------
    # CHECK EXISTING SERVING PATIENT
    # -----------------------------------------------------

    current_serving = (
        Appointment.query
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == date.today(),
            Appointment.status == 'NOW SERVING'
        )
        .first()
    )


    if current_serving:

        flash(
            f'Token #{current_serving.token_number} '
            f'is already being served.',
            'warning'
        )

        return redirect(
            url_for('doctor.dashboard')
        )


    # -----------------------------------------------------
    # VALID STATUS
    # -----------------------------------------------------

    if appointment.status not in [
        'BOOKED',
        'CHECKED-IN',
        'WAITING'
    ]:

        flash(
            'This appointment cannot be started.',
            'warning'
        )

        return redirect(
            url_for('doctor.dashboard')
        )


    # -----------------------------------------------------
    # START CONSULTATION
    # -----------------------------------------------------

    appointment.status = 'NOW SERVING'

    db.session.commit()


    flash(
        f'Token #{appointment.token_number} '
        f'is now being served.',
        'success'
    )


    return redirect(
        url_for('doctor.dashboard')
    )


# =========================================================
# COMPLETE CONSULTATION
# =========================================================

@doctor_bp.route(
    '/complete/<int:id>',
    methods=['POST']
)
@login_required
def complete(id):

    if current_user.role != 'doctor':
        return redirect(url_for('index'))


    doctor = current_user.doctor_profile

    appointment = Appointment.query.get_or_404(id)


    # -----------------------------------------------------
    # SECURITY CHECK
    # -----------------------------------------------------

    if appointment.doctor_id != doctor.id:

        flash(
            'You are not authorized to modify this appointment.',
            'danger'
        )

        return redirect(
            url_for('doctor.dashboard')
        )


    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    appointment.status = 'COMPLETED'

    appointment.completed_at = datetime.utcnow()

    db.session.commit()


    flash(
        f'Consultation for Token #{appointment.token_number} '
        f'marked as COMPLETED.',
        'success'
    )


    return redirect(
        url_for('doctor.dashboard')
    )