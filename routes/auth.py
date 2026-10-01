from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from models import db
from models.user import User, Patient


auth_bp = Blueprint(
    'auth',
    __name__
)


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route(
    '/login',
    methods=['GET', 'POST']
)
def login():

    # -----------------------------------------------------
    # Already logged in
    # -----------------------------------------------------

    if current_user.is_authenticated:

        if current_user.role == 'patient':
            return redirect(
                url_for('patient.dashboard')
            )

        elif current_user.role == 'doctor':
            return redirect(
                url_for('doctor.dashboard')
            )

        elif current_user.role == 'staff':
            return redirect(
                url_for('staff.dashboard')
            )

        return redirect(
            url_for('index')
        )

    # -----------------------------------------------------
    # Login form
    # -----------------------------------------------------

    if request.method == 'POST':

        email = request.form.get(
            'email',
            ''
        ).strip().lower()

        password = request.form.get(
            'password',
            ''
        ).strip()

        # Basic validation

        if not email or not password:

            flash(
                'Please enter both email and password.',
                'warning'
            )

            return render_template(
                'login.html'
            )

        # Find user

        user = User.query.filter_by(
            email=email
        ).first()

        # -------------------------------------------------
        # USER NOT FOUND
        # -------------------------------------------------

        if not user:

            flash(
                'No account found with this email address.',
                'danger'
            )

            return render_template(
                'login.html'
            )

        # -------------------------------------------------
        # PASSWORD CHECK
        # -------------------------------------------------

        if not user.check_password(password):

            flash(
                'Incorrect password. Please try again.',
                'danger'
            )

            return render_template(
                'login.html'
            )

        # -------------------------------------------------
        # DOCTOR PROFILE CHECK
        # -------------------------------------------------

        if user.role == 'doctor':

            if not user.doctor_profile:

                flash(
                    'Doctor profile is not configured for this account.',
                    'danger'
                )

                return render_template(
                    'login.html'
                )

        # -------------------------------------------------
        # PATIENT PROFILE CHECK
        # -------------------------------------------------

        if user.role == 'patient':

            if not user.patient_profile:

                flash(
                    'Patient profile is not configured for this account.',
                    'danger'
                )

                return render_template(
                    'login.html'
                )

        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        login_user(user)

        flash(
            f'Welcome, {user.full_name}!',
            'success'
        )

        # -------------------------------------------------
        # ROLE BASED REDIRECT
        # -------------------------------------------------

        if user.role == 'patient':

            return redirect(
                url_for('patient.dashboard')
            )

        elif user.role == 'doctor':

            return redirect(
                url_for('doctor.dashboard')
            )

        elif user.role == 'staff':

            return redirect(
                url_for('staff.dashboard')
            )

        # Unknown role

        logout_user()

        flash(
            'Invalid account role.',
            'danger'
        )

        return redirect(
            url_for('auth.login')
        )

    return render_template(
        'login.html'
    )


# =========================================================
# REGISTER
# =========================================================

@auth_bp.route(
    '/register',
    methods=['GET', 'POST']
)
def register():

    if request.method == 'POST':

        email = request.form.get(
            'email',
            ''
        ).strip().lower()

        password = request.form.get(
            'password',
            ''
        ).strip()

        full_name = request.form.get(
            'full_name',
            ''
        ).strip()

        phone = request.form.get(
            'phone',
            ''
        ).strip()

        age = request.form.get(
            'age',
            type=int
        )

        gender = request.form.get(
            'gender',
            ''
        ).strip()

        village = request.form.get(
            'village',
            ''
        ).strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not email or not password or not full_name:

            flash(
                'Please fill all required fields.',
                'warning'
            )

            return redirect(
                url_for('auth.register')
            )

        # -------------------------------------------------
        # DUPLICATE EMAIL
        # -------------------------------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                'Email address is already registered.',
                'warning'
            )

            return redirect(
                url_for('auth.register')
            )

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        new_user = User(
            email=email,
            role='patient',
            full_name=full_name,
            phone=phone
        )

        new_user.set_password(
            password
        )

        db.session.add(
            new_user
        )

        db.session.flush()

        # -------------------------------------------------
        # CREATE PATIENT PROFILE
        # -------------------------------------------------

        new_patient = Patient(
            user_id=new_user.id,
            age=age,
            gender=gender,
            village=village
        )

        db.session.add(
            new_patient
        )

        db.session.commit()

        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        login_user(
            new_user
        )

        flash(
            'Registration successful! Welcome to GramCare.',
            'success'
        )

        return redirect(
            url_for('patient.dashboard')
        )

    return render_template(
        'register.html'
    )


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route('/logout')
@login_required
def logout():

    logout_user()

    flash(
        'You have been logged out safely.',
        'info'
    )

    return redirect(
        url_for('index')
    )