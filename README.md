# 🏥 Doctor Appointment Management System

A full-stack Doctor Appointment System built using Django, Django REST Framework, React.js, and PostgreSQL.  
Deployed on Render with Neon Database and Cloudinary integration.

---

## 🚀 Appointment Lifecycle

Available → Booked → Patient Present → Seen by Doctor → Completed

---

# 👤 Patient Features

- Register / Login (JWT Based)
- View Doctors
- Book Appointment
- Track Appointment Status
- Check-in (Mark Present)
- Cancel / Reschedule Appointment
- View Doctor Notes & Prescription
- Download Prescription PDF (ReportLab)
- Update Profile

---

# 👨‍⚕️ Doctor Features

- Register / Login
- Set Availability (Days & Time)
- View Today’s Appointments
- See Patient Status
- Mark Patient Present
- Start Consultation
- Write Notes / Prescription
- Upload Reports
- Mark Appointment Completed
- Manage Profile

---

# 🛠 Tech Stack

Backend: Django + Django REST Framework  
Frontend: React.js  
Database: PostgreSQL (Neon)  
Authentication: JWT  
Deployment: Render  
Cloud Storage: Cloudinary  
PDF Generation: ReportLab  

---

# 📦 Major Dependencies

Django==4.2.11  
djangorestframework==3.15.2  
reportlab==4.4.9  
psycopg[binary]>=3.2  
gunicorn>=21.2.0  
whitenoise==6.11.0  
cloudinary  
django-cloudinary-storage  

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/AJX008-Ankita/doctor_appointment.git
cd doctor_appointment

2️⃣ Create Virtual Environment
python -m venv venv

3️⃣ Activate
venv\Scripts\activate

4️⃣ Install Dependencies
pip install -r requirements.txt

5️⃣ Configure Environment Variables (.env)
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=your_neon_database_url
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

6️⃣ Run Migrations
python manage.py migrate

7️⃣ Run Server
python manage.py runserver
