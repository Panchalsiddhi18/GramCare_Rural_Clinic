from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User

import os

if os.environ.get("VERCEL"):
    app = Flask(__name__, instance_path="/tmp/instance")
else:
    app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
from routes.auth import auth_bp
from routes.patient import patient_bp
from routes.staff import staff_bp
from routes.doctor import doctor_bp
from routes.api import api_bp
from routes.analytics import analytics_bp

app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(api_bp)
app.register_blueprint(analytics_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live_queue')
def live_queue_page():
    return render_template('live_queue.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

