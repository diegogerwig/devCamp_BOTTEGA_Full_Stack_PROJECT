# TimeTracer - Work Hours Management System

![TimeTracer](https://img.shields.io/badge/TimeTracer-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11.8-green)
![Node](https://img.shields.io/badge/Node-20.19.0-green)
![React](https://img.shields.io/badge/React-19.1.1-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

Complete work hours management system with role-based access control, check-in/check-out tracking, and team management by departments.

---

## 📋 Table of Contents

- [Project Links](#-project-links)
- [Description](#-description)
- [Features](#-features)
- [Technologies](#️-technologies)
- [Architecture](#️-architecture)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Roles and Permissions](#-roles-and-permissions)
- [Database Structure](#-database-structure)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Contact](#-contact-and-support)
- [License](#-license)

---

## 🔗 Project Links

| Resource | URL |
|---------|-----|
| **Frontend (Production)** | [https://time-tracer-bottega-front.onrender.com](https://time-tracer-bottega-front.onrender.com) |
| **Backend API** | [https://time-tracer-bottega-back.onrender.com](https://time-tracer-bottega-back.onrender.com) |
| **API Documentation** | [https://time-tracer-bottega-back.onrender.com/api/docs](https://time-tracer-bottega-back.onrender.com/api/docs) |
| **GitHub Repository** | [https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT](https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT) |
| **Capstone Requirements** | [Capstone Requirements](./doc/Capstone%20Requirements.md) |

---

## 📖 Description

**TimeTracer** is a complete web-based work hours management system deployed on Render.com that allows:

- **Check-in/check-out tracking** with precise timestamps in local time
- **User management** with three differentiated roles (Admin, Manager, Worker)
- **Team control** by departments
- **Real-time statistics** visualization
- **Edit and delete** records based on permissions
- **Secure authentication** with JWT tokens
- **Persistent PostgreSQL database**

---

## ✨ Features

### 🔐 Authentication System
- Secure login with JWT tokens (24-hour expiration)
- Session persistence via localStorage
- Email and password validation
- Role-based route protection
- Automatic token refresh

### 👥 User Management (Admin)
- Create users with different roles
- Edit user information (name, email, password, role, department)
- Delete users and their records
- Assign departments
- Cannot edit/delete own user

### ⏰ Work Hours Tracking
- **Check-in/Check-out** with automatic timestamp
- One active record at a time per user
- Validation to prevent multiple open entries
- Automatic calculation of worked hours
- Edit and delete based on permissions (Admin/Manager only)
- Local timezone preservation (no UTC conversion)
- Notes field for additional information

### 📊 Personalized Dashboards

**Admin Dashboard:**
- Complete system view with statistics
- User management (create, edit, delete)
- Access to all time entries
- Edit and delete any record

**Manager Dashboard:**
- Personal time tracking (check-in/check-out)
- View and manage team members' records
- Cannot edit/delete own time entries
- Department-specific view
- Team roster display

**Worker Dashboard:**
- Personal work hours tracking
- Check-in/check-out functionality
- View own entry history
- Total hours worked statistics
- Real-time duration display for active shifts

### 🔒 Permission Control
- Granular permissions by role
- Edit and delete restrictions
- Department validation for managers
- Self-edit/delete protection
- One open entry per user at a time

---

## 🛠️ Technologies

### Frontend
- **React 19.1.1** - UI Library
- **Vite 7.1.2** - Build tool and dev server
- **Tailwind CSS 3.4.17** - Utility-first CSS framework
- **Axios 1.12.1** - HTTP client for API requests
- **React Context API** - State management
- **ESLint 9.33.0** - Code linting

### Backend
- **Flask 2.3.3** - Python web framework
- **PostgreSQL 17 (Render)** - Production database
- **SQLAlchemy 3.0.5** - ORM for database operations
- **pg8000 1.30.3** - Pure-Python PostgreSQL driver
- **Flask-JWT-Extended 4.6.0** - JWT authentication
- **Flask-Bcrypt 1.0.1** - Password hashing
- **Flask-CORS 4.0.0** - CORS handling
- **Gunicorn 21.2.0** - WSGI HTTP server

### Infrastructure
- **Render.com** - Cloud hosting platform
- **PostgreSQL (Managed)** - Persistent database
- **Git/GitHub** - Version control
- **Python 3.11.8** - Backend runtime
- **Node.js 20.19.0** - Frontend build environment

---

## 🏗️ Architecture

```
timetracer/
├── backend/                    # Flask API
│   ├── app.py                  # Main application with all routes
│   ├── auth.py                 # Authentication decorators
│   ├── requirements.txt        # Python dependencies
│   ├── Procfile                # Render deployment config
│   ├── runtime.txt             # Python version specification
│   ├── data/
│   │   └── mock_data.py        # Mock users for testing
│   └── src/
│       ├── connection_db.py    # Database connection setup
│       ├── init_db.py          # Database initialization
│       ├── models.py           # SQLAlchemy models
│       └── date_utils.py       # Date/time utility functions
│
├── frontend/                   # React SPA
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   └── Login.jsx      # Login form component
│   │   ├── views/             # Role-based dashboards
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── ManagerDashboard.jsx
│   │   │   └── WorkerDashboard.jsx
│   │   ├── context/           # React Context
│   │   │   └── AuthContext.jsx
│   │   ├── services/          # API services
│   │   │   └── api.js         # Axios configuration
│   │   ├── utils/             # Utilities
│   │   │   └── timeUtils.js   # Date/time helpers
│   │   ├── App.jsx            # Main app component
│   │   ├── main.jsx           # Entry point
│   │   └── index.css          # Tailwind imports
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── .env.example               # Environment variables template
├── .gitignore
├── .node-version
├── LICENSE
├── README.md
└── render.yaml                # Render deployment config
```

---

## 🔌 API Endpoints

### Base URL
```
Production: https://time-tracer-bottega-back.onrender.com
```

### Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation and live statistics |
| `/api/health` | GET | Health check for monitoring |
| `/api/docs` | GET | Complete API documentation |

### Authentication Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/login` | POST | No | User login - Returns JWT token |
| `/api/auth/me` | GET | JWT | Get current authenticated user |

### User Management Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/users` | GET | JWT | List users (filtered by role permissions) |
| `/api/users` | POST | JWT (Admin) | Create new user |
| `/api/users/:id` | PUT | JWT (Admin) | Update user (cannot edit self) |
| `/api/users/:id` | DELETE | JWT (Admin) | Delete user and all records |

### Time Entries Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/time-entries` | GET | JWT | List entries (filtered by role) |
| `/api/time-entries` | POST | JWT | Create/update entry (check-in/out) |
| `/api/time-entries/:id` | PUT | JWT (Manager/Admin) | Edit entry (not own for managers) |
| `/api/time-entries/:id` | DELETE | JWT (Manager/Admin) | Delete entry (not own for managers) |

### Using the API

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

**Example with curl:**
```bash
# Login
curl -X POST https://time-tracer-bottega-back.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@timetracer.com","password":"your_password"}'

# Use token
curl https://time-tracer-bottega-back.onrender.com/api/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 👤 Roles and Permissions

### 🔴 Admin
**Full system access**

**Permissions:**
- ✅ View all system users
- ✅ Create, edit, and delete any user
- ✅ View all time entries
- ✅ Edit and delete any time entry
- ✅ Access all statistics

**Restrictions:**
- ❌ Cannot edit their own user
- ❌ Cannot delete their own user

### 🔵 Manager
**Department management**

**Permissions:**
- ✅ View users in their department
- ✅ View time entries from their department
- ✅ Edit team member entries (except own)
- ✅ Delete team member entries (except own)
- ✅ Record their own work hours (check-in/check-out)
- ✅ View team statistics

**Restrictions:**
- ❌ Cannot view users from other departments
- ❌ Cannot create new users
- ❌ Cannot edit their own time entries
- ❌ Cannot delete their own time entries

### 🟢 Worker
**Personal work hours management**

**Permissions:**
- ✅ View their own information
- ✅ Record check-in (shift start)
- ✅ Record check-out (shift end)
- ✅ View their entry history
- ✅ One active entry at a time

**Restrictions:**
- ❌ Cannot view other users' information
- ❌ Cannot edit time entries (own or others')
- ❌ Cannot delete time entries
- ❌ Cannot create multiple open entries

---

## 📊 Database Structure

### Table: users

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary Key |
| name | VARCHAR(100) | User name |
| email | VARCHAR(120) | Unique email |
| users_password | VARCHAR(255) | Hashed password (bcrypt) |
| role | VARCHAR(20) | admin, manager, worker |
| department | VARCHAR(50) | Department name |
| status | VARCHAR(20) | active, inactive |
| created_at | DATETIME | Creation timestamp |

### Table: time_entries

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary Key |
| user_id | INTEGER | Foreign Key → users.id |
| date | DATE | Entry date (YYYY-MM-DD) |
| check_in | DATETIME | Clock-in time (local time) |
| check_out | DATETIME | Clock-out time (local time, nullable) |
| total_hours | FLOAT | Hours worked (nullable) |
| notes | TEXT | Optional notes |
| created_at | DATETIME | Creation timestamp |

**Indexes:**
- `user_id` - Fast user lookups
- `date` - Date filtering
- `check_out IS NULL` - Find open entries

**Constraints:**
- One open entry per user at a time
- Foreign key cascade on user deletion

---

## 🔐 Security

### Implemented Security Features

✅ **JWT Authentication**
- Tokens with 24-hour expiration
- Secure storage in localStorage
- Automatic refresh on frontend
- Token validation on every protected request

✅ **Password Security**
- Bcrypt hashing with automatic salt
- Never store plain-text passwords
- Secure password requirements

✅ **Authorization**
- Role-based access control (RBAC)
- Route-level permission decorators
- Department-based filtering for managers
- Self-edit/delete prevention

✅ **Input Validation**
- Email format validation
- Required field validation
- Data type checking
- SQL injection prevention via ORM

✅ **CORS Configuration**
- Controlled origins whitelist
- Specific allowed methods
- Secure headers configuration

✅ **API Security**
- Protected endpoints require authentication
- 401/403 error handling
- Request/response interceptors
- Timeout configuration

### Security Best Practices

⚠️ **For Production:**
1. Use environment variables for all secrets
2. Enable HTTPS (Render provides this automatically)
3. Implement rate limiting on API endpoints
4. Add request logging for audit trails
5. Regular security updates for dependencies
6. Periodic JWT secret rotation
7. Implement account lockout after failed attempts
8. Use secure session management
9. Add CSP headers
10. Regular security audits

---

## 🐛 Troubleshooting

### Frontend Issues

**Problem:** Cannot connect to backend
```
Network Error or CORS error
```

**Solution:**
1. Verify backend is running at: https://time-tracer-bottega-back.onrender.com/api/health
2. Check browser console for specific error messages
3. Clear browser cache and localStorage:
```javascript
localStorage.clear()
```
4. Verify CORS configuration in backend

---

**Problem:** 401 Unauthorized on all requests

**Solution:**
1. Token may be expired (24h validity)
2. Clear localStorage and login again
3. Check token format in Authorization header
4. Verify backend is running

---

**Problem:** Login button not working

**Solution:**
1. Check email format validation
2. Verify credentials in .env file
3. Check browser console for errors
4. Ensure backend API is accessible

---

### Backend Issues

**Problem:** Database connection error

**Solution:**
1. Check Render dashboard for service status
2. Verify PostgreSQL database is active
3. Check DATABASE_URL environment variable
4. Review backend logs in Render dashboard

---

**Problem:** Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.11.8
```

---

### Timezone Issues

**Problem:** Time displays incorrectly

**Solution:**
- Application preserves local timezone
- No UTC conversion on timestamps
- Verify browser timezone settings
- Check system time configuration
- Times stored as-is in database

---

### Build Issues

**Frontend build fails:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Backend deployment fails:**
```bash
# Check Python version in runtime.txt
# Verify all dependencies in requirements.txt
# Check Render build logs
```

---

## 📞 Contact 

### Author
**Diego Gerwig López**

- GitHub: [@diegogerwig](https://github.com/diegogerwig)
- LinkedIn: [Diego Gerwig](https://linkedin.com/in/diegogerwig)

---

## 📜 License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Diego Gerwig López

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

*TimeTracer - Making work hour tracking simple and efficient*