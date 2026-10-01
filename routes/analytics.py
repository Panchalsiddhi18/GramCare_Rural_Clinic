from flask import Blueprint, render_template
from flask_login import login_required
from models import db
from models.appointment import Appointment
from models.clinic import Clinic
from datetime import date

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def index():
    today = date.today()
    total_appts = Appointment.query.filter_by(appointment_date=today).count()
    completed = Appointment.query.filter_by(appointment_date=today, status='COMPLETED').count()
    cancelled = Appointment.query.filter_by(appointment_date=today, status='CANCELLED').count()
    noshow = Appointment.query.filter_by(appointment_date=today, status='NO-SHOW').count()
    
    # Priority breakdown for visual graph
    urgent = Appointment.query.filter_by(appointment_date=today, priority='URGENT').count()
    elderly = Appointment.query.filter_by(appointment_date=today, priority='ELDERLY').count()
    pregnant = Appointment.query.filter_by(appointment_date=today, priority='PREGNANT').count()
    normal = Appointment.query.filter_by(appointment_date=today, priority='NORMAL').count()

    return render_template('analytics.html', 
                           total=total_appts,
                           completed=completed,
                           cancelled=cancelled,
                           noshow=noshow,
                           p_urgent=urgent,
                           p_elderly=elderly,
                           p_pregnant=pregnant,
                           p_normal=normal)

