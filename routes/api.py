from flask import Blueprint, jsonify, request
from models import db
from models.clinic import Clinic, Doctor
from models.appointment import Appointment
from datetime import date

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/queue/<int:clinic_id>')
def get_queue(clinic_id):
    today = date.today()
    clinic = Clinic.query.get_or_404(clinic_id)
    
    serving = Appointment.query.filter_by(clinic_id=clinic_id, appointment_date=today, status='NOW SERVING').first()
    
    waiting = Appointment.query.filter(
        Appointment.clinic_id == clinic_id,
        Appointment.appointment_date == today,
        Appointment.status.in_(['CHECKED-IN', 'WAITING'])
    ).all()
    waiting.sort(key=lambda a: a.calculate_effective_priority())

    next_tokens = [a.token_number for a in waiting[:3]]

    return jsonify({
        'clinic_name': clinic.name,
        'current_serving_token': serving.token_number if serving else None,
        'current_patient_name': serving.patient.user.full_name if serving else 'None',
        'next_tokens': next_tokens,
        'total_waiting': len(waiting),
        'avg_wait_per_patient': clinic.avg_consultation_time,
        'est_total_queue_time': len(waiting) * clinic.avg_consultation_time
    })

@api_bp.route('/demo/reset', methods=['POST'])
def reset_demo():
    # Helper endpoint for hackathon demo reset
    import seed
    seed.seed_database()
    return jsonify({'status': 'success', 'message': 'Demo database re-seeded successfully.'})

