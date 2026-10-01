# GramCare — SIH Professional UI Edition

Flask + SQLAlchemy rural clinic coordination demo with role-based dashboards, smart queue priority, patient booking, doctor workstation, staff dispatch and analytics.

## Windows quick start
```powershell
cd "C:\path\to\GramCare_SIH_Professional"
py -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python init_db.py
python seed.py
python app.py
```
Open http://127.0.0.1:5000

Demo: patient@demo.com / demo123, staff@demo.com / demo123, doctor@demo.com / demo123.
