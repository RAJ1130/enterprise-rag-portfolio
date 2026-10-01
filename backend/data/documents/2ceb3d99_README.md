# 🩺 Smart Health System

A full-stack healthcare application:
- **Backend:** Django 5 + Django REST Framework + JWT auth (SQLite by default, Postgres-ready)
- **Frontend:** React 18 (React Router, Axios, Context API, Recharts, Lucide icons)

Roles: **Patient** and **Doctor**, each with a tailored dashboard.
Features: registration/login, doctor directory, appointment booking, appointment status
management (confirm/complete/cancel), and medical records.

## Design system

The v2 frontend uses a deliberate visual identity instead of a generic admin-panel look:
- **Palette:** warm paper background, deep pine-green sidebar, clinical teal accent, muted gold and rust for status states
- **Type:** Newsreader (serif) for headings — reads like a medical record — paired with IBM Plex Sans for UI text and IBM Plex Mono for numeric data (fees, times)
- **Layout:** fixed dark sidebar navigation, a dashboard hero panel for the next appointment, a Recharts activity trend, and timeline-style (not card-grid) views for appointments and records

---

## 📁 Project Structure

```
smart-health-system/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── smart_health/        # Django project (settings, urls)
│   ├── accounts/            # Custom user model + JWT auth endpoints
│   └── healthcare/          # Doctors, patients, appointments, medical records
└── frontend/
    ├── package.json
    ├── public/index.html
    └── src/
        ├── api/axios.js       # Axios instance w/ JWT interceptor
        ├── context/AuthContext.js
        ├── components/        # Sidebar, ProtectedRoute
        ├── pages/              # Login, Register, Dashboard, Doctors, Appointments, Records
        ├── App.js
        └── index.css           # Design tokens + component styles
```

---

## 🖥️ Running this locally in VS Code

### 0. Prerequisites
- **Python 3.11+**
- **Node.js 18+** and npm
- **VS Code** with the Python extension (Microsoft)

### 1. Open the project
`File → Open Folder…` → select `smart-health-system`.

### 2. Backend (Django) — Terminal 1

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Runs at **http://127.0.0.1:8000** — admin at **http://127.0.0.1:8000/admin/**

> In VS Code, select the `venv` interpreter from the bottom status bar so imports resolve.

### 3. Frontend (React) — Terminal 2

```bash
cd frontend
npm install
npm start
```
Opens **http://localhost:3000** automatically, already wired to the Django API.

### 4. Try it
1. Register a **Doctor** account and a **Patient** account at `/register`.
2. As the doctor, fill in their profile via `/admin/healthcare/doctorprofile/add/` (specialization, fee, etc.) — this admin step is the one manual piece; see "Next steps" below to replace it with a form.
3. As the patient, go to **Doctors** and book an appointment.
4. As the doctor, confirm/complete it under **Appointments**, then add a **Medical Record**.

---

## 🔀 Pushing this to your own GitHub repo

This project already has a local git repo with an initial commit. To push it to your own
GitHub:

```bash
# 1. Create an empty repo on GitHub first (no README/gitignore), then:
cd smart-health-system
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

If GitHub asks for a password, use a **Personal Access Token** (Settings → Developer
settings → Personal access tokens) rather than your account password — GitHub no longer
accepts account passwords over HTTPS git.

To keep committing as you build:
```bash
git add -A
git commit -m "Describe what you changed"
git push
```

---

## 🔌 API Overview

All endpoints are prefixed with `/api/`. Auth uses JWT (`Authorization: Bearer <token>`).

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register/` | POST | Create a new user (patient or doctor) |
| `/api/auth/login/` | POST | Get access + refresh tokens |
| `/api/auth/refresh/` | POST | Refresh an expired access token |
| `/api/auth/me/` | GET | Get the logged-in user's profile |
| `/api/doctors/` | GET, POST | List / create doctor profiles |
| `/api/patients/` | GET, POST | List / create patient profiles (scoped per user) |
| `/api/appointments/` | GET, POST | List / book appointments (scoped per role) |
| `/api/appointments/{id}/` | PATCH | Update appointment status |
| `/api/records/` | GET, POST | List / create medical records |

Role-based access is enforced in `healthcare/views.py` — patients only see their own
data; doctors only see their own patients/appointments/records.

---

## 🗄️ Switching to PostgreSQL (optional)

1. `pip install psycopg2-binary`
2. In `backend/smart_health/settings.py`, swap the SQLite `DATABASES` block for the
   commented Postgres one.
3. Add `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` to `.env`.
4. `python manage.py migrate`

---

## 🚀 Suggested next steps
- Replace the admin-panel doctor-profile step with an in-app "Complete your profile" form
- Add email notifications for appointment confirmations
- Add file uploads for lab reports (`MEDIA_URL` is already wired up)
- Deploy backend (Render/Railway) + frontend (Vercel/Netlify); update `API_BASE_URL` in `src/api/axios.js`

Built with Django REST Framework + React. Happy coding! 🎉
