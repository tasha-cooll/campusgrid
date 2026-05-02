# campusgrid

Centralized facility booking and conflict resolution platform for university extarcurricular spaces - UEAB Senior Project INSY 492

<div align="center">

<img src="https://img.shields.io/badge/version-0.1.0--alpha-1F3864?style=for-the-badge" alt="Version"/>
<img src="https://img.shields.io/badge/status-In%20Development-2E75B6?style=for-the-badge" alt="Status"/>
<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"/>
<img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL"/>

<br/><br/>

# 🏛️ CampusGrid

### Extracurricular Facility Utilization Conflict Resolver

_A centralized, intelligent scheduling platform for university extracurricular spaces._

**INSY 492 — Senior Project · University of Eastern Africa Baraton**
**Student:** Win Wanjiru Gatacha · **ID:** SGATWI2311
**Supervisor:** Dr Roselyne Nyamwamu · **Instructor:** Mr Omari Dickson Mogaka

---

</div>

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [The Problem](#-the-problem)
- [System Architecture](#-system-architecture)
- [Modules](#-modules)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Development Roadmap](#-development-roadmap)
- [Progress Log](#-progress-log)
- [API Overview](#-api-overview)
- [Role Permissions](#-role-permissions)
- [Contributing / Supervisor Notes](#-contributing--supervisor-notes)
- [License](#-license)

---

## 🎯 About the Project

**CampusGrid** is a web-based facility booking and conflict resolution system built specifically for the extracurricular spaces at the University of Eastern Africa Baraton. It replaces fragmented spreadsheets, paper timetables and email chains with a single, role-aware platform that handles the full lifecycle of a facility booking — from request to approval to reporting.

The system's defining feature is its **conflict detection engine**: when a requested time slot is already occupied, CampusGrid does not simply reject the booking — it automatically surfaces the **three nearest available alternative slots**, resolving potential disputes before they occur.

> _"Before CampusGrid, clubs found out about double-bookings on the day of the event. After CampusGrid, the conflict never reaches a human."_

---

## 🔍 The Problem

Managing extracurricular facility bookings at UEAB currently relies on:

- Manual spreadsheets maintained by different departmental secretaries
- Email correspondence with no structured approval process
- Paper timetables pinned to notice boards around campus

This results in:

| Problem                          | Impact                                                       |
| -------------------------------- | ------------------------------------------------------------ |
| Double-booking conflicts         | Clubs arrive to find another group already using their venue |
| Underutilized slots              | Available time goes unfilled because no one can see it       |
| Opaque approval process          | Requesters have no visibility into their application status  |
| No usage data                    | Administration cannot make data-driven facility decisions    |
| No conflict resolution mechanism | Disputes are resolved manually and inconsistently            |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CampusGrid Platform                      │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────────────┐ │
│  │  Club Leader │    │Sports Director│    │   Administrator    │ │
│  │  (Requester) │    │  (Approver)  │    │  (Full Control)    │ │
│  └──────┬───────┘    └──────┬───────┘    └────────┬───────────┘ │
│         │                   │                     │             │
│  ┌──────▼───────────────────▼─────────────────────▼───────────┐ │
│  │              User Authentication Module                     │ │
│  │         JWT · Role-Based Access · Session Management        │ │
│  └──────────────────────────┬────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────┐  ┌────────▼──────────┐  ┌──────────────────┐ │
│  │   Facility   │  │  Booking Request  │  │    Approval      │ │
│  │  Management  ├─►│     Module        ├─►│    Workflow      │ │
│  │              │  │                   │  │                  │ │
│  └──────────────┘  └────────┬──────────┘  └────────┬─────────┘ │
│                             │                       │           │
│                    ┌────────▼──────────┐            │           │
│                    │ Conflict Detection│            │           │
│                    │    & Resolution   │            │           │
│                    │  Engine           │            │           │
│                    └────────┬──────────┘            │           │
│                             │                       │           │
│  ┌──────────────┐  ┌────────▼──────────┐  ┌────────▼─────────┐ │
│  │  Reports &   │  │  Calendar / Grid  │  │  Notification    │ │
│  │  Analytics   │  │      View         │  │  Layer           │ │
│  └──────┬───────┘  └────────┬──────────┘  └────────┬─────────┘ │
│         │                   │                       │           │
│  ┌──────▼───────────────────▼───────────────────────▼─────────┐ │
│  │                    MySQL Database                           │ │
│  │     Facilities · Bookings · Users · Roles · Audit Log       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Modules

| #   | Module                              | Description                                              | Status     |
| --- | ----------------------------------- | -------------------------------------------------------- | ---------- |
| 1   | **User Authentication**             | JWT login, role assignment, session management           | 🔲 Planned |
| 2   | **Facility Management**             | Admin CRUD for venues — capacity, hours, location        | 🔲 Planned |
| 3   | **Booking Request**                 | Submit requests with date, time, purpose, attendance     | 🔲 Planned |
| 4   | **Conflict Detection & Resolution** | Detects overlaps, suggests 3 nearest free slots          | 🔲 Planned |
| 5   | **Approval Workflow**               | Director review queue, approve/reject with notifications | 🔲 Planned |
| 6   | **Calendar & Scheduling View**      | Interactive visual grid of all bookings in real time     | 🔲 Planned |
| 7   | **Reports & Analytics**             | Monthly utilization reports, peak demand, conflict logs  | 🔲 Planned |
| 8   | **Notification Layer**              | Email + in-app alerts on all booking status changes      | 🔲 Planned |
| 9   | **Audit Log**                       | Timestamped record of every booking action and actor     | 🔲 Planned |

**Status key:** 🔲 Planned · 🔄 In Progress · ✅ Complete · 🧪 Testing

---

## 🛠️ Tech Stack

| Layer           | Technology                                | Purpose                                          |
| --------------- | ----------------------------------------- | ------------------------------------------------ |
| Frontend        | HTML, CSS, Bootstrap 5                    | Responsive UI layout                             |
| Frontend JS     | React (CDN) / HTMX                        | Reactive calendar and live availability          |
| Backend         | Python 3.11 + Django 5                    | Application logic, ORM, admin panel              |
| API             | Django REST Framework                     | RESTful endpoints for all modules                |
| Database        | MySQL 8.0                                 | Relational data — bookings, users, facilities    |
| Auth            | JWT (via `djangorestframework-simplejwt`) | Stateless, secure role-based access              |
| Notifications   | Django Signals + SMTP                     | Event-driven email and in-app alerts             |
| Design          | Figma                                     | Wireframes and UI prototyping                    |
| Deployment      | Railway / Render (free tier)              | Live URL accessible to supervisor and evaluators |
| Version Control | Git + GitHub                              | Project history and milestone tracking           |

---

## 📁 Project Structure

```
campusgrid/
│
├── core/                    # Django project settings and root URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                # Module 1 — User authentication & roles
│   ├── models.py            # CustomUser, Role
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
│
├── facilities/              # Module 2 — Facility management
│   ├── models.py            # Facility, FacilityHours
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
│
├── bookings/                # Modules 3 & 4 — Booking + conflict detection
│   ├── models.py            # Booking, ConflictLog
│   ├── views.py
│   ├── serializers.py
│   ├── conflict_engine.py   # Core conflict detection & slot suggestion logic
│   └── urls.py
│
├── approvals/               # Module 5 — Approval workflow
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── reports/                 # Modules 7 & 9 — Analytics + audit log
│   ├── models.py            # AuditLog
│   ├── views.py
│   └── urls.py
│
├── notifications/           # Module 8 — Notification layer
│   ├── signals.py           # Django signal handlers
│   ├── email.py
│   └── utils.py
│
├── frontend/                # Static assets and React components
│   ├── static/
│   └── templates/
│
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
├── manage.py
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- Node.js 18+ (for frontend tooling, optional)
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/campusgrid.git
cd campusgrid
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

Your `.env` file should contain:

```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
DATABASE_NAME=campusgrid_db
DATABASE_USER=your_mysql_user
DATABASE_PASSWORD=your_mysql_password
DATABASE_HOST=localhost
DATABASE_PORT=3306
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 5. Set up the database

```bash
# Create the MySQL database
mysql -u root -p -e "CREATE DATABASE campusgrid_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations
python manage.py migrate

# Create a superuser (admin)
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

---

## 🗺️ Development Roadmap

The project is developed incrementally. Each milestone begins with documentation, then implementation, then testing.

```
Phase 1 — Foundation
├── ✅ Project proposal and scope definition
├── ✅ README and repository setup
├── ✅ Django project scaffold and app creation
├── ✅ Database schema design (ERD)
└── 🔄 Base templates and static files

Phase 2 — Authentication & Facility Management
├── ✅ Custom user model with roles
├── ✅ JWT login / logout / token refresh
├── ✅ Role-based permission middleware
├── ✅ Facility CRUD (Admin)
└── ✅ Facility listing view (all roles)

Phase 3 — Booking & Conflict Engine
├── 🔲 Booking request form and API endpoint
├── 🔲 Conflict detection algorithm
├── 🔲 Three-slot alternative suggestion logic
└── 🔲 Booking status lifecycle (pending → approved/rejected)

Phase 4 — Approval Workflow & Notifications
├── 🔲 Approval queue view (Sports Director)
├── 🔲 Approve / reject actions
├── 🔲 Django signals for booking events
├── 🔲 In-app notification model
└── 🔲 Email notification via SMTP

Phase 5 — Calendar, Reports & Audit
├── 🔲 Interactive calendar grid view
├── 🔲 Monthly utilization report generation
├── 🔲 Conflict log and audit trail
└── 🔲 Admin analytics dashboard

Phase 6 — Polish & Deployment
├── 🔲 Figma wireframe alignment pass
├── 🔲 Responsive UI testing (mobile + tablet)
├── 🔲 Deployment to Railway / Render
├── 🔲 Final documentation and user guide
└── 🔲 Project submission
```

---

## 📈 Progress Log

| Date       | Phase   | Milestone                                                   | Notes          |
| ---------- | ------- | ----------------------------------------------------------- | -------------- |
| 2026-03-26 | Phase 1 | Repository created and README written                       | Initial commit |
| 2026-05-02 | Phase 1 | Django scaffold, settings, DB config, CustomUser model      | v0.1.0         |
| 2026-05-02 | Phase 2 | User authentication — JWT, roles, permissions, registration | v0.2.0         |
| 2026-05-02 | Phase 2 | Facility management — models, hours, admin, API endpoints   | v0.3.0         |
| —          | —       | —                                                           | —              |

_This table is updated with every significant commit._

---

## 🔌 API Overview

> ⚠️ API documentation will be populated as each module is implemented. The full API will be documented using Django REST Framework's built-in browsable API at `/api/`.

| Endpoint                        | Method     | Description                       | Auth Required    |
| ------------------------------- | ---------- | --------------------------------- | ---------------- |
| `/api/auth/login/`              | POST       | Obtain JWT token pair             | No               |
| `/api/auth/refresh/`            | POST       | Refresh access token              | No               |
| `/api/facilities/`              | GET        | List all facilities               | Yes              |
| `/api/facilities/:id/`          | GET        | Facility detail + availability    | Yes              |
| `/api/bookings/`                | GET, POST  | List bookings / submit request    | Yes              |
| `/api/bookings/:id/`            | GET, PATCH | Booking detail / update status    | Yes (role-gated) |
| `/api/bookings/check-conflict/` | POST       | Run conflict detection for a slot | Yes              |
| `/api/approvals/`               | GET        | Pending approvals queue           | Approver+        |
| `/api/approvals/:id/approve/`   | POST       | Approve a booking                 | Approver+        |
| `/api/approvals/:id/reject/`    | POST       | Reject a booking                  | Approver+        |
| `/api/reports/utilization/`     | GET        | Monthly utilization report        | Admin            |
| `/api/reports/audit-log/`       | GET        | Full audit trail                  | Admin            |

---

## 👥 Role Permissions

| Feature                    | Club Leader (Requester) | Sports Director (Approver) | Administrator |
| -------------------------- | ----------------------- | -------------------------- | ------------- |
| View facility availability | ✅                      | ✅                         | ✅            |
| Submit booking request     | ✅                      | ✅                         | ✅            |
| View own bookings          | ✅                      | ✅                         | ✅            |
| View all bookings          | ❌                      | ✅                         | ✅            |
| Approve / reject bookings  | ❌                      | ✅                         | ✅            |
| Add / edit facilities      | ❌                      | ❌                         | ✅            |
| Override any booking       | ❌                      | ❌                         | ✅            |
| View utilization reports   | ❌                      | Partial                    | ✅            |
| View audit log             | ❌                      | ❌                         | ✅            |
| Manage user roles          | ❌                      | ❌                         | ✅            |

---

## 📝 Contributing / Supervisor Notes

This repository documents the full development lifecycle of the CampusGrid senior project. Each feature is developed on a separate branch and merged into `main` via a pull request upon completion.

**Branch naming convention:**

```
feature/user-authentication
feature/facility-management
feature/booking-engine
feature/conflict-detection
feature/approval-workflow
feature/calendar-view
feature/reports-dashboard
feature/notifications
feature/deployment
```

**Commit message convention:**

```
feat:   new feature or module
fix:    bug fix
docs:   documentation update
test:   test additions or changes
refactor: code restructuring without behavior change
chore:  dependency or config updates
```

**For the supervisor:** All project milestones, design decisions and implementation notes are documented in the [Wiki](../../wiki) tab of this repository. The live deployment URL will be added here once Phase 6 is complete.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**CampusGrid** · UEAB Senior Project INSY 492 · 2026

_Built with purpose, documented with care._

</div>
