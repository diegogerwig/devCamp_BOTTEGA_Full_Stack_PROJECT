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
- [Local Installation](#-local-installation)
- [Configuration](#️-configuration)
- [API Usage](#-api-usage)
- [Roles and Permissions](#-roles-and-permissions)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [License](#-license)

---

## 🔗 Project Links

| Resource | URL |
|---------|-----|
| **Frontend (Production)** | [https://time-tracer-bottega-front.onrender.com](https://time-tracer-bottega-front.onrender.com) |
| **Backend API** | [https://time-tracer-bottega-back.onrender.com](https://time-tracer-bottega-back.onrender.com) |
| **API Docs** | [https://time-tracer-bottega-back.onrender.com/](https://time-tracer-bottega-back.onrender.com/) |
| **GitHub Repo** | [https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT](https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT) |
| **Subject** | [Capstone Requirements](./doc/Capstone%20Requirements.md) |
| **Proposal** | [Capstone Proposal](./doc/Capstone%20Proposal.md) |

---

## 📖 Description

**TimeTracer** is a complete web-based work hours management system that allows:

- **Check-in/check-out tracking** with precise timestamps in local time
- **User management** with three differentiated roles (Admin, Manager, Worker)
- **Team control** by departments
- **Real-time statistics** visualization
- **Edit and delete** records based on permissions
- **Secure authentication** with JWT tokens
- **Persistent database** on PostgreSQL

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
- **PostgreSQL** - Database (production)
- **SQLite** - Database (development)
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **Flask-Bcrypt** - Password hashing
- **Flask-CORS** - CORS handling
- **Gunicorn** - WSGI server

### Infrastructure
- **Render.com** - Hosting (frontend and backend)
- **PostgreSQL (Render)** - Persistent database
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
│   │   │   └── Login.jsx
│   │   ├── views/           # Role-based dashboards
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── ManagerDashboard.jsx
│   │   │   └── WorkerDashboard.jsx
│   │   ├── context/         # Context API
│   │   │   └── AuthContext.jsx
│   │   ├── services/        # API services
│   │   │   └── api.js
│   │   ├── utils/           # Utilities
│   │   │   └── timeUtils.js
│   │   ├── App.jsx          # Main component
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── doc/                       # Documentation
│   ├── Capstone Requirements.md
│   └── Capstone Proposal.md
│
├── .gitignore
├── .node-version
├── LICENSE
├── README.md
└── render.yaml               # Deployment config
```

---

## 📦 Local Installation

### Prerequisites
- Python 3.11+
- Node.js 20.19+
- PostgreSQL (optional, uses SQLite by default)

### 1. Clone the repository
```bash
git clone https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT.git
cd devCamp_BOTTEGA_Full_Stack_PROJECT
```

### 2. Backend Setup

```bash
# Enter backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
cp .env.example .env
# Edit .env with your configurations

# Start server
python app.py
```

Backend will be available at `http://localhost:5000`

### 3. Frontend Setup

```bash
# Enter frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
cp .env.example .env
# Edit .env with URLs and credentials

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## ⚙️ Configuration

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://username:password@host:port/database_name

# Flask
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Demo Users (optional)
ADMIN_PASSWORD=admin123
MANAGER_PASSWORD=manager123
WORKER_PASSWORD=worker123
```

### Frontend (.env)

```env
# Backend API URL
VITE_API_URL=http://localhost:5000

# Demo Credentials (shown on login)
VITE_DEMO_ADMIN_EMAIL=admin@timetracer.com
VITE_DEMO_ADMIN_PASSWORD=admin123
VITE_DEMO_MANAGER_EMAIL=juan@company.com
VITE_DEMO_MANAGER_PASSWORD=manager123
VITE_DEMO_WORKER_EMAIL=maria@company.com
VITE_DEMO_WORKER_PASSWORD=worker123
```

---

## 🔌 API Usage

### Public Endpoints

#### 1. View Documentation
```bash
# View statistics and complete documentation
curl https://time-tracer-bottega-back.onrender.com/
```

#### 2. Health Check
```bash
# Verify server status
curl https://time-tracer-bottega-back.onrender.com/api/health
```

### Authentication

#### Login
```bash
# Login and get token
curl -X POST https://time-tracer-bottega-back.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@timetracer.com",
    "password": "your_password"
  }'
```

**Successful response:**
```json
{
  "message": "Login exitoso",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "Admin TimeTracer",
    "email": "admin@timetracer.com",
    "role": "admin",
    "department": "IT",
    "status": "active"
  }
}
```

#### Get Current User
```bash
# View authenticated user information
curl https://time-tracer-bottega-back.onrender.com/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### User Management

#### List Users
```bash
# List users based on role permissions
curl https://time-tracer-bottega-back.onrender.com/api/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Create User (Admin only)
```bash
curl -X POST https://time-tracer-bottega-back.onrender.com/api/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New User",
    "email": "new@company.com",
    "password": "password123",
    "role": "worker",
    "department": "Operations"
  }'
```

#### Update User (Admin only)
```bash
curl -X PUT https://time-tracer-bottega-back.onrender.com/api/users/3 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated User",
    "email": "updated@company.com",
    "role": "manager",
    "department": "Sales"
  }'
```

#### Delete User (Admin only)
```bash
curl -X DELETE https://time-tracer-bottega-back.onrender.com/api/users/3 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Time Entries

#### List Time Entries
```bash
# List entries based on role permissions
curl https://time-tracer-bottega-back.onrender.com/api/time-entries \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Create Entry (Check-in)
```bash
curl -X POST https://time-tracer-bottega-back.onrender.com/api/time-entries \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "date": "2025-10-08",
    "check_in": "2025-10-08T08:00:00.000",
    "check_out": null,
    "notes": "Start of shift"
  }'
```

#### Update Entry (Check-out)
```bash
curl -X POST https://time-tracer-bottega-back.onrender.com/api/time-entries \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "date": "2025-10-08",
    "check_in": "2025-10-08T08:00:00.000",
    "check_out": "2025-10-08T17:00:00.000",
    "total_hours": 9.0,
    "notes": "Shift completed"
  }'
```

#### Edit Entry (Manager/Admin only)
```bash
curl -X PUT https://time-tracer-bottega-back.onrender.com/api/time-entries/5 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "check_in": "2025-10-08T08:30:00.000",
    "check_out": "2025-10-08T17:30:00.000",
    "total_hours": 9.0
  }'
```

#### Delete Entry (Manager/Admin only)
```bash
curl -X DELETE https://time-tracer-bottega-back.onrender.com/api/time-entries/5 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Complete Bash Script

```bash
#!/bin/bash

# TimeTracer API - Complete example script

BASE_URL="https://time-tracer-bottega-back.onrender.com"

# 1. Login and save token
echo "🔐 Logging in..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@timetracer.com","password":"your_password"}')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')

if [ "$TOKEN" == "null" ]; then
    echo "❌ Login error"
    echo $RESPONSE | jq '.'
    exit 1
fi

echo "✅ Token obtained: ${TOKEN:0:20}..."

# 2. View current user
echo -e "\n👤 Current user:"
curl -s "$BASE_URL/api/auth/me" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '{id, name, email, role, department}'

# 3. List users
echo -e "\n👥 System users:"
curl -s "$BASE_URL/api/users" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.users[] | {id, name, role, department}'

# 4. List time entries
echo -e "\n⏰ Time entries:"
curl -s "$BASE_URL/api/time-entries" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.time_entries[] | {id, user_id, date, check_in, check_out, total_hours}'

# 5. Create new user (admin only)
echo -e "\n➕ Creating new user..."
curl -s -X POST "$BASE_URL/api/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@company.com",
    "password": "test123",
    "role": "worker",
    "department": "IT"
  }' \
  | jq '{message, user: {id, name, email, role}}'

echo -e "\n✅ Script completed"
```

---

## 👤 Roles and Permissions

### 🔴 Admin
**Description:** Full system access

**Can:**
- ✅ View all system users
- ✅ Create, edit, and delete any user
- ✅ View all time entries
- ✅ Edit and delete any time entry
- ✅ Access all statistics

**Cannot:**
- ❌ Edit their own user
- ❌ Delete their own user

### 🔵 Manager
**Description:** Department management

**Can:**
- ✅ View users in their department
- ✅ View time entries from their department
- ✅ Edit team member entries
- ✅ Delete team member entries
- ✅ Record their own work hours (check-in/check-out)

**Cannot:**
- ❌ View users from other departments
- ❌ Create new users
- ❌ Edit their own time entries
- ❌ Delete their own time entries

### 🟢 Worker
**Description:** Personal work hours management

**Can:**
- ✅ View their own information
- ✅ Record check-in (shift start)
- ✅ Record check-out (shift end)
- ✅ View their entry history

**Cannot:**
- ❌ View other users' information
- ❌ Edit time entries (own or others')
- ❌ Delete time entries
- ❌ Create multiple open entries

---

## 🚀 Deployment

The project is configured to deploy automatically on **Render.com**.

### Render Configuration

#### 1. Backend (Web Service)
```yaml
name: timetracer-backend
runtime: python
buildCommand: cd backend && pip install -r requirements.txt
startCommand: cd backend && gunicorn app:app
healthCheckPath: /api/health
envVars:
  - PYTHON_VERSION: 3.11.8
  - FLASK_ENV: production
  - SECRET_KEY: [auto-generated]
  - JWT_SECRET_KEY: [auto-generated]
  - DATABASE_URL: [PostgreSQL URL]
```

#### 2. Frontend (Static Site)
```yaml
name: timetracer-frontend
runtime: static
buildCommand: cd frontend && npm install && npm run build
staticPublishPath: ./frontend/dist
envVars:
  - NODE_VERSION: 20.19.0
```

### Manual Deployment

```bash
# 1. Commit changes
git add .
git commit -m "feat: update application"
git push origin main

# 2. Render will automatically detect changes
# and deploy both services
```

---

## 🧪 Testing

### Testing with Postman

1. **Import collection**: Download [TimeTracer.postman_collection.json](#)
2. **Configure variables**:
   - `base_url`: `https://time-tracer-bottega-back.onrender.com`
   - `token`: (obtained automatically from login)
3. **Execute requests** in workflow order

### Testing with Thunder Client (VS Code)

1. Install Thunder Client extension
2. Create new request
3. Configure headers:
   - `Content-Type: application/json`
   - `Authorization: Bearer YOUR_TOKEN`
4. Save requests in collections for reuse

### Manual Testing

#### Complete Testing Flow

1. **Login**
   ```bash
   POST /api/auth/login
   Body: {"email": "admin@timetracer.com", "password": "your_pass"}
   → Copy access_token
   ```

2. **View users**
   ```bash
   GET /api/users
   Header: Authorization: Bearer <token>
   ```

3. **Create entry**
   ```bash
   POST /api/time-entries
   Header: Authorization: Bearer <token>
   Body: {"user_id": 3, "date": "2025-10-08", "check_in": "2025-10-08T08:00:00.000"}
   ```

4. **Verify entry**
   ```bash
   GET /api/time-entries
   Header: Authorization: Bearer <token>
   ```

---

## 🐛 Troubleshooting

### Backend won't start

**Problem:** Error starting Flask
```bash
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

---

**Problem:** Database error
```bash
OperationalError: no such table: users
```

**Solution:**
Backend creates tables automatically on first start. If it persists:
```bash
# Delete SQLite file and restart
rm backend/timetracer.db
python backend/app.py
```

---

### Frontend doesn't connect to Backend

**Problem:** CORS error or network error

**Solution:**
1. Verify backend is running
2. Check URL in `frontend/src/services/api.js`:
```javascript
const API_URL = 'http://localhost:5000'; // For local development
```

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

### Timezone Errors

**Problem:** Hours display incorrectly

**Solution:**
The app handles timestamps in user's local time. If you see incorrect hours:
1. Verify browser timezone configuration
2. Timestamps are saved preserving local time (no UTC conversion)

---

### Node.js Version Error on Render

**Problem:** 
```
Node.js version 18.20.8 has reached end-of-life
```

**Solution:**
Update `.node-version`:
```bash
echo "20.19.0" > .node-version
git commit -am "chore: update Node.js to v20"
git push
```

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

## 📞 Contact and Support

### Author
**Diego Gerwig López**

- GitHub: [@diegogerwig](https://github.com/diegogerwig)
- Email: diego.gerwig@example.com
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