from app import app
from models import db

def init():
    with app.app_context():
        db.create_all()
        print("Database tables initialized successfully.")

if __name__ == '__main__':
    init()

