# TimeTracer - Work Hours Management System

![TimeTracer](https://img.shields.io/badge/TimeTracer-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![Node](https://img.shields.io/badge/Node-20.19-green)
![React](https://img.shields.io/badge/React-19.1-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

Complete work hours management system with role-based access control, check-in/check-out tracking, and team management by departments.

---

## 📋 Table of Contents

- [Project Links](#-project-links)
- [Description](#-description)
- [Features](#-features)
- [Technologies](#️-technologies)
- [Architecture](#️-architecture)
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
| **API Documentation** | [https://time-tracer-bottega-back.onrender.com/](https://time-tracer-bottega-back.onrender.com/) |
| **GitHub Repository** | [https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT](https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT) |
| **Capstone Requirements** | [Capstone Requirements](./doc/Capstone%20Requirements.md) |
| **Capstone Proposal** | [Capstone Proposal](./doc/Capstone%20Proposal.md) |

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
- Secure login with JWT tokens
- Session persistence
- Email and password validation
- Role-based route protection

### 👥 User Management (Admin)
- Create users with different roles
- Edit user information
- Delete users and their records
- Assign departments

### ⏰ Work Hours Tracking
- **Check-in/Check-out** with automatic timestamp
- Multiple records per day
- Open record validation
- Automatic calculation of worked hours
- Edit and delete based on permissions
- Local timezone preservation

### 📊 Personalized Dashboards
- **Admin**: Complete system view with statistics
- **Manager**: Team and department management
- **Worker**: Personal work hours tracking

### 🔒 Permission Control
- Granular permissions by role
- Edit and delete restrictions
- Department validation for managers
- Self-edit/delete protection

---

## 🛠️ Technologies

### Frontend
- **React 19.1** - UI Library
- **Vite 7.1** - Build tool
- **Tailwind CSS 4.1** - Styling
- **Axios** - HTTP client
- **React Context API** - State management

### Backend
- **Flask 2.3** - Web framework
- **PostgreSQL (Render)** - Production database
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **Flask-Bcrypt** - Password hashing
- **Flask-CORS** - CORS handling
- **Gunicorn** - WSGI server

### Infrastructure
- **Render.com** - Cloud hosting platform
- **PostgreSQL (Managed)** - Persistent database
- **Git/GitHub** - Version control

---

## 🏗️ Architecture

```
timetracer/
├── backend/                    # Flask API
│   ├── app.py                 # Main application
│   ├── auth.py                # Authentication decorators
│   ├── requirements.txt       # Python dependencies
│   ├── Procfile              # Render config
│   └── runtime.txt           # Python version
│
├── frontend/                   # React SPA
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── views/           # Role-based dashboards
│   │   ├── context/         # Context API
│   │   ├── services/        # API services
│   │   ├── utils/           # Utilities
│   │   ├── App.jsx          # Main component
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── doc/                       # Documentation
├── .gitignore
├── LICENSE
├── README.md
└── render.yaml               # Deployment config
```

---

## 🔌 API Endpoints

### Base URL
```
https://time-tracer-bottega-back.onrender.com
```

### Public Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | API documentation and live statistics |
| `/api/health` | GET | No | Health check for monitoring |

### Authentication Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/login` | POST | No | User login - Returns JWT token |
| `/api/auth/me` | GET | JWT | Get current authenticated user |

**Login Request Body:**
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Login Response:**
```json
{
  "message": "Login exitoso",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "User Name",
    "email": "user@example.com",
    "role": "admin",
    "department": "IT",
    "status": "active"
  }
}
```

### User Management Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/users` | GET | JWT | List users (filtered by role permissions) |
| `/api/users` | POST | JWT (Admin) | Create new user |
| `/api/users/:id` | PUT | JWT (Admin) | Update user (cannot edit self) |
| `/api/users/:id` | DELETE | JWT (Admin) | Delete user and all records |

**Create User Request:**
```json
{
  "name": "New User",
  "email": "new@company.com",
  "password": "password123",
  "role": "worker",
  "department": "Operations"
}
```

### Time Entries Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/time-entries` | GET | JWT | List entries (filtered by role) |
| `/api/time-entries` | POST | JWT | Create/update entry (check-in/out) |
| `/api/time-entries/:id` | PUT | JWT (Manager/Admin) | Edit entry (not own records for managers) |
| `/api/time-entries/:id` | DELETE | JWT (Manager/Admin) | Delete entry (not own records for managers) |

**Create Entry (Check-in) Request:**
```json
{
  "user_id": 3,
  "date": "2025-10-08",
  "check_in": "2025-10-08T08:00:00.000",
  "check_out": null,
  "notes": "Start of shift"
}
```

**Update Entry (Check-out) Request:**
```json
{
  "user_id": 3,
  "date": "2025-10-08",
  "check_in": "2025-10-08T08:00:00.000",
  "check_out": "2025-10-08T17:00:00.000",
  "total_hours": 9.0,
  "notes": "Shift completed"
}
```

### Using the API

**Authentication:**
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

**Example with curl:**
```bash
# Login
curl -X POST https://time-tracer-bottega-back.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"your_password"}'

# Use token in subsequent requests
curl https://time-tracer-bottega-back.onrender.com/api/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Example with JavaScript:**
```javascript
// Login
const response = await fetch('https://time-tracer-bottega-back.onrender.com/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'your@email.com', password: 'your_password' })
});
const { access_token } = await response.json();

// Use token
const users = await fetch('https://time-tracer-bottega-back.onrender.com/api/users', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

---

## 👤 Roles and Permissions

### 🔴 Admin
**Description:** Full system access

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
**Description:** Department management

**Permissions:**
- ✅ View users in their department
- ✅ View time entries from their department
- ✅ Edit team member entries
- ✅ Delete team member entries
- ✅ Record their own work hours (check-in/check-out)

**Restrictions:**
- ❌ Cannot view users from other departments
- ❌ Cannot create new users
- ❌ Cannot edit their own time entries
- ❌ Cannot delete their own time entries

### 🟢 Worker
**Description:** Personal work hours management

**Permissions:**
- ✅ View their own information
- ✅ Record check-in (shift start)
- ✅ Record check-out (shift end)
- ✅ View their entry history

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
| users_password | VARCHAR(255) | Hashed password |
| role | VARCHAR(20) | admin, manager, worker |
| department | VARCHAR(50) | Department |
| status | VARCHAR(20) | active, inactive |
| created_at | DATETIME | Creation date |

### Table: time_entries

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary Key |
| user_id | INTEGER | Foreign Key → users.id |
| date | DATE | Entry date |
| check_in | DATETIME | Clock-in time (local) |
| check_out | DATETIME | Clock-out time (local) |
| total_hours | FLOAT | Hours worked |
| notes | TEXT | Optional notes |
| created_at | DATETIME | Creation date |

**Indexes:**
- `user_id` for fast user lookups
- `date` for date filtering
- `check_out IS NULL` for open entries

---

## 🔐 Security

### Implemented Practices

✅ **JWT Authentication**
- Tokens with 24-hour expiration
- Automatic refresh on frontend
- Secure storage in localStorage

✅ **Password Hashing**
- Bcrypt with automatic salt
- Never store plain-text passwords

✅ **Permission Validation**
- Decorators on each endpoint
- Backend role verification
- Department control for managers

✅ **Data Validation**
- Email format validation
- Input sanitization
- Duplicate prevention

✅ **CORS Configuration**
- Allowed origins whitelist
- Specific allowed headers
- Restricted HTTP methods

### Additional Recommendations

⚠️ **For Production:**
1. Use environment variables for secrets
2. Enable HTTPS (Render does this automatically)
3. Implement rate limiting
4. Add audit logs
5. Periodic JWT secret rotation

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
3. Clear browser cache and localStorage

---

**Problem:** 401 Unauthorized on all requests

**Solution:**
1. Verify token is valid
2. Clear localStorage:
```javascript
// In browser console
localStorage.clear()
```
3. Login again

---

### Backend Issues

**Problem:** Database connection error

**Solution:**
This is a Render.com deployment - if you see database errors:
1. Check Render dashboard for service status
2. Verify PostgreSQL database is active
3. Check environment variables are set correctly

---

### Timezone Errors

**Problem:** Hours display incorrectly

**Solution:**
The app handles timestamps in user's local time:
1. Verify browser timezone configuration
2. Timestamps are saved preserving local time (no UTC conversion)
3. Check system time settings

---

## 📞 Contact and Support

### Author
**Diego Gerwig López**

- GitHub: [@diegogerwig](https://github.com/diegogerwig)
- LinkedIn: [Diego Gerwig](https://linkedin.com/in/diegogerwig)

### Report Issues

If you find a bug or have a suggestion:

1. Search in [existing Issues](https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT/issues)
2. If it doesn't exist, [create a new issue](https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT/issues/new)
3. Describe the problem in detail:
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Browser/system information

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

*Project developed as Capstone Project for devCAMP BOTTEGA 2025*