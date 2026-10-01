from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_login import login_required, current_user

from models.user import Patient
from models import db
from models.clinic import Clinic, Doctor
from models.appointment import Appointment
from models.notification import Notification

from datetime import date, datetime


patient_bp = Blueprint(
    'patient',
    __name__,
    url_prefix='/patient'
)


# =========================================================
# PATIENT DASHBOARD
# =========================================================

@patient_bp.route('/dashboard')
@login_required
def dashboard():

    if current_user.role != 'patient':
        return redirect(url_for('index'))

    patient = current_user.patient_profile
    today = date.today()

    # -----------------------------------------------------
    # ACTIVE APPOINTMENT
    # -----------------------------------------------------

    active_appointment = (
        Appointment.query
        .filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date == today,
            Appointment.status.in_([
                'BOOKED',
                'CHECKED-IN',
                'WAITING',
                'NOW SERVING'
            ])
        )
        .order_by(
            Appointment.token_number.asc()
        )
        .first()
    )

    queue_info = None

    # -----------------------------------------------------
    # SHOW APPOINTMENT INFORMATION
    # FOR ALL ACTIVE STATUSES
    # -----------------------------------------------------

    if active_appointment:

        clinic = active_appointment.clinic
        doctor = active_appointment.doctor

        # Current serving token
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

        current_token = (
            serving.token_number
            if serving
            else 0
        )

        # Patients currently waiting
        waiting_list = (
            Appointment.query
            .filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == today,
                Appointment.status.in_([
                    'BOOKED',
                    'CHECKED-IN',
                    'WAITING',
                    'NOW SERVING'
                ])
            )
            .order_by(
                Appointment.token_number.asc()
            )
            .all()
        )

        # -------------------------------------------------
        # FIND PATIENTS AHEAD
        # -------------------------------------------------

        patients_ahead = 0

        for appointment in waiting_list:

            if appointment.id == active_appointment.id:
                break

            if appointment.status in [
                'BOOKED',
                'CHECKED-IN',
                'WAITING',
                'NOW SERVING'
            ]:
                patients_ahead += 1

        # If patient is already being served,
        # nobody should be shown ahead.
        if active_appointment.status == 'NOW SERVING':
            patients_ahead = 0

        estimated_wait = (
            patients_ahead *
            clinic.avg_consultation_time
        )

        queue_info = {
            'current_token': current_token,
            'your_token': active_appointment.token_number,
            'patients_ahead': patients_ahead,
            'est_wait': estimated_wait,
            'priority': active_appointment.priority,
            'doctor_name': doctor.user.full_name,
            'doctor_specialization': doctor.specialization,
            'clinic_name': clinic.name,
            'status': active_appointment.status,
            'time_slot': active_appointment.time_slot
        }

    # -----------------------------------------------------
    # APPOINTMENT HISTORY
    # -----------------------------------------------------

    history = (
        Appointment.query
        .filter_by(
            patient_id=patient.id
        )
        .order_by(
            Appointment.created_at.desc()
        )
        .all()
    )

    # -----------------------------------------------------
    # NOTIFICATIONS
    # -----------------------------------------------------

    notifications = (
        Notification.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .limit(5)
        .all()
    )

    return render_template(
    'patient_dashboard.html',
    active=active_appointment,
    active_appointment=active_appointment,
    queue_info=queue_info,
    history=history,
    notifications=notifications
)

# =========================================================
# HEALTH RECORD
# =========================================================

@patient_bp.route('/health-record')
@login_required
def health_record():

    if current_user.role != 'patient':
        return redirect(url_for('auth.login'))

    patient = Patient.query.filter_by(
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        'health_record.html',
        patient=patient,
        history=patient.appointments
    )


# =========================================================
# EDIT HEALTH RECORD
# =========================================================

@patient_bp.route(
    '/health-record/edit',
    methods=['GET', 'POST']
)
@login_required
def edit_health_record():

    if current_user.role != 'patient':
        return redirect(url_for('index'))

    patient = Patient.query.filter_by(
        user_id=current_user.id
    ).first_or_404()

    if request.method == 'POST':

        patient.age = request.form.get(
            'age',
            type=int
        )

        patient.gender = request.form.get(
            'gender',
            ''
        ).strip()

        patient.village = request.form.get(
            'village',
            ''
        ).strip()

        patient.abha_id = request.form.get(
            'abha_id',
            ''
        ).strip()

        patient.blood_group = request.form.get(
            'blood_group',
            ''
        ).strip()

        patient.emergency_contact = request.form.get(
            'emergency_contact',
            ''
        ).strip()

        patient.allergies = request.form.get(
            'allergies',
            ''
        ).strip()

        patient.current_medications = request.form.get(
            'current_medications',
            ''
        ).strip()

        patient.medical_history = request.form.get(
            'medical_history',
            ''
        ).strip()

        db.session.commit()

        flash(
            'Health profile updated successfully.',
            'success'
        )

        return redirect(
            url_for('patient.health_record')
        )

    return render_template(
        'edit_health_record.html',
        patient=patient
    )


# =========================================================
# BOOK APPOINTMENT
# =========================================================

@patient_bp.route(
    '/book',
    methods=['GET', 'POST']
)
@login_required
def book():

    if current_user.role != 'patient':
        return redirect(url_for('index'))

    patient = current_user.patient_profile
    today = date.today()

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == 'POST':

        doctor_id = request.form.get(
            'doctor_id',
            type=int
        )

        clinic_id = request.form.get(
            'clinic_id',
            type=int
        )

        specialization = request.form.get(
            'specialization',
            ''
        ).strip()

        time_slot = request.form.get(
            'time_slot',
            '09:00 AM - 10:00 AM'
        )

        # -------------------------------------------------
        # DOCTOR
        # -------------------------------------------------

        doctor = Doctor.query.get(doctor_id)

        if not doctor:

            flash(
                'Please select a valid doctor.',
                'danger'
            )

            return redirect(
                url_for('patient.book')
            )

        # -------------------------------------------------
        # CLINIC
        # -------------------------------------------------

        clinic = Clinic.query.get(clinic_id)

        if not clinic:

            flash(
                'Please select a valid clinic.',
                'danger'
            )

            return redirect(
                url_for('patient.book')
            )

        # -------------------------------------------------
        # DOCTOR + CLINIC VALIDATION
        # -------------------------------------------------

        if doctor.clinic_id != clinic.id:

            flash(
                'Selected doctor is not available at this clinic.',
                'danger'
            )

            return redirect(
                url_for('patient.book')
            )

        # -------------------------------------------------
        # DOCTOR AVAILABILITY
        # -------------------------------------------------

        if not doctor.is_available:

            flash(
                'This doctor is currently unavailable. '
                'Please select another doctor.',
                'warning'
            )

            return redirect(
                url_for('patient.book')
            )

        # -------------------------------------------------
        # SPECIALIZATION
        # -------------------------------------------------

        if (
            specialization
            and doctor.specialization != specialization
        ):

            flash(
                'Please select a doctor from the '
                'selected specialization.',
                'danger'
            )

            return redirect(
                url_for('patient.book')
            )

        # -------------------------------------------------
        # EXISTING APPOINTMENT
        # -------------------------------------------------

        existing = (
            Appointment.query
            .filter_by(
                patient_id=patient.id,
                appointment_date=today
            )
            .filter(
                Appointment.status.notin_([
                    'CANCELLED',
                    'COMPLETED'
                ])
            )
            .first()
        )

        if existing:

            flash(
                'You already have an active appointment '
                'scheduled for today.',
                'warning'
            )

            return redirect(
                url_for('patient.dashboard')
            )

        # -------------------------------------------------
        # TOKEN
        # -------------------------------------------------

        max_token = (
            db.session.query(
                db.func.max(
                    Appointment.token_number
                )
            )
            .filter_by(
                doctor_id=doctor.id,
                appointment_date=today
            )
            .scalar()
            or 0
        )

        next_token = max_token + 1

        # -------------------------------------------------
        # CREATE APPOINTMENT
        # -------------------------------------------------

        new_appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            clinic_id=clinic.id,
            appointment_date=today,
            time_slot=time_slot,
            status='BOOKED',
            token_number=next_token,
            priority='NORMAL'
        )

        db.session.add(new_appointment)
        db.session.commit()

        # -------------------------------------------------
        # NOTIFICATION
        # -------------------------------------------------

        doctor_name = doctor.user.full_name

        notification = Notification(
            user_id=current_user.id,
            message=(
                f"Appointment confirmed with "
                f"Dr. {doctor_name.replace('Dr. ', '')} "
                f"at {clinic.name}. "
                f"Your Token Number is #{next_token}."
            ),
            category='BOOKING'
        )

        db.session.add(notification)
        db.session.commit()

        flash(
            f'Appointment booked successfully! '
            f'Token #{next_token} with Dr. {doctor_name}.',
            'success'
        )

        return redirect(
            url_for('patient.dashboard')
        )

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    clinics = (
        Clinic.query
        .order_by(
            Clinic.name.asc()
        )
        .all()
    )

    doctors = (
        Doctor.query
        .join(Doctor.user)
        .order_by(
            Doctor.specialization.asc(),
            Doctor.id.asc()
        )
        .all()
    )

    specializations = sorted(
        {
            doctor.specialization
            for doctor in doctors
            if doctor.specialization
        }
    )

    return render_template(
        'booking.html',
        clinics=clinics,
        doctors=doctors,
        specializations=specializations
    )


# =========================================================
# DOCTOR API
# =========================================================

@patient_bp.route('/doctors')
@login_required
def doctors_api():

    if current_user.role != 'patient':
        return jsonify([]), 403

    clinic_id = request.args.get(
        'clinic_id',
        type=int
    )

    specialization = request.args.get(
        'specialization',
        ''
    ).strip()

    query = Doctor.query.filter(
        Doctor.is_available.is_(True)
    )

    if clinic_id:

        query = query.filter(
            Doctor.clinic_id == clinic_id
        )

    if specialization:

        query = query.filter(
            Doctor.specialization == specialization
        )

    doctors = (
        query
        .join(Doctor.user)
        .order_by(
            Doctor.specialization.asc(),
            Doctor.id.asc()
        )
        .all()
    )

    result = []

    for doctor in doctors:

        result.append({
            'id': doctor.id,
            'name': doctor.user.full_name,
            'specialization': doctor.specialization,
            'clinic_id': doctor.clinic_id,
            'room_number': doctor.room_number,
            'available': doctor.is_available
        })

    return jsonify(result)


# =========================================================
# CANCEL APPOINTMENT
# =========================================================

@patient_bp.route(
    '/cancel/<int:id>',
    methods=['POST']
)
@login_required
def cancel(id):

    appointment = Appointment.query.get_or_404(id)

    if (
        appointment.patient.user_id == current_user.id
        and appointment.status in [
            'BOOKED',
            'CHECKED-IN',
            'WAITING'
        ]
    ):

        appointment.status = 'CANCELLED'

        db.session.commit()

        flash(
            'Appointment cancelled successfully.',
            'info'
        )

    return redirect(
        url_for('patient.dashboard')
    )
