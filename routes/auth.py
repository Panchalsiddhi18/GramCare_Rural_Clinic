from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User, Patient

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Successfully logged in.', 'success')
            if user.role == 'patient':
                return redirect(url_for('patient.dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff.dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor.dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', '')
        village = request.form.get('village', '')

        if User.query.filter_by(email=email).first():
            flash('Email address is already registered.', 'warning')
            return redirect(url_for('auth.register'))

        new_user = User(email=email, role='patient', full_name=full_name, phone=phone)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        new_patient = Patient(user_id=new_user.id, age=age, gender=gender, village=village)
        db.session.add(new_patient)
        db.session.commit()

        login_user(new_user)
        flash('Registration successful! Welcome to GramCare.', 'success')
        return redirect(url_for('patient.dashboard'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))

