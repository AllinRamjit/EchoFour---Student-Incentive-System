# Student Incentive Platform

## Overview
This is a Flask-based web application that helps tertiary institutions track and reward student participation. The platform captures volunteer or co-curricular hours, validates them through staff approvals, and converts approved time into accolades and leaderboard rankings.

## Recent Changes (December 2, 2025)
- **Web UI Implementation**: Implemented comprehensive web interface based on wireframe specifications
  - Created modern base.html template with purple theme and responsive design
  - Added Login and Registration pages with Student/Staff role selection
  - Implemented Student Dashboard with navigation, hours summary, and recent activities
  - Created My Accolades page showing earned and upcoming milestones
  - Added Pending Confirmations page for students to view their requests
  - Implemented My Hours and Activities page with status filters
  - Created Activity History page with milestone tracking
  - Added Staff Dashboard with pending requests list
  - Implemented Log Student Hours form for staff
  - Created Student Leaderboard with rankings and progress bars
  - Updated 401 and index pages with new styling
- Successfully configured the project for Replit environment
- Updated Python dependencies (upgraded gevent to 24.2.1+ for Python 3.12 compatibility)
- Fixed model indentation issues in Student and Staff classes
- Corrected `__init__` and `__repr__` method definitions in Student and Staff models
- Configured Gunicorn to run on port 5000 (required for Replit webview)
- Initialized database with sample data
- Configured deployment for autoscale deployment target
- Application is now running successfully on Replit

## Project Architecture

### Technology Stack
- **Backend Framework**: Flask 2.3.3
- **Database**: SQLite (default), PostgreSQL supported
- **ORM**: Flask-SQLAlchemy 3.1.1
- **Authentication**: Flask-JWT-Extended 4.4.4
- **Server**: Gunicorn 20.1.0 with gevent workers
- **Migrations**: Flask-Migrate 3.1.0
- **Testing**: pytest 7.0.1

### Project Structure
```
App/
├── controllers/     # Business logic and request handlers
├── models/         # Database models (User, Student, Staff, Request, LoggedHours)
├── views/          # Route definitions and blueprints
├── templates/      # HTML templates
├── static/         # CSS, JavaScript, and static assets
├── tests/          # Unit and integration tests
├── config.py       # Configuration loader
└── main.py         # Application factory

wsgi.py             # Entry point with CLI commands
gunicorn_config.py  # Gunicorn server configuration
requirements.txt    # Python dependencies
```

### Database Models
1. **User** (base class)
   - Polymorphic inheritance for Student and Staff
   - Fields: user_id, username, email, password (hashed), role

2. **Student** (inherits from User)
   - One-to-many with LoggedHours and Request
   - Can request hours, view accolades, check leaderboard

3. **Staff** (inherits from User)
   - One-to-many with LoggedHours
   - Can approve/deny student hour requests

4. **Request**
   - Student hour confirmation requests
   - Statuses: pending, approved, denied

5. **LoggedHours**
   - Approved hours for students
   - Linked to both student and approving staff member

6. **Activity**
   - Activity history tracking for students

## Running the Application

### Development Mode
The application runs automatically in Replit. The workflow is configured to run:
```bash
gunicorn -c gunicorn_config.py wsgi:app
```

### Initialization
To initialize/reset the database:
```bash
flask init
```

### Flask CLI Commands
Available commands for managing the application:

#### General Commands
- `flask init` - Initialize database with sample data
- `flask listUsers` - List all users
- `flask listStaff` - List all staff members
- `flask listStudents` - List all students
- `flask listRequests` - List all requests
- `flask listApprovedRequests` - List approved requests
- `flask listPendingRequests` - List pending requests
- `flask listDeniedRequests` - List denied requests
- `flask listloggedHours` - List all logged hours

#### Student Commands
- `flask student create` - Create a new student
- `flask student hours` - View total approved hours
- `flask student requestHours` - Request hour confirmation
- `flask student viewmyRequests` - View all personal requests
- `flask student viewmyAccolades` - View earned accolades
- `flask student viewLeaderboard` - View student leaderboard
- `flask student viewActivityHistory` - View activity history

#### Staff Commands
- `flask staff create` - Create a new staff member
- `flask staff requests` - View all pending requests
- `flask staff approveRequest` - Approve a student request
- `flask staff denyRequest` - Deny a student request
- `flask staff viewLeaderboard` - View student leaderboard

#### Testing Commands
- `flask test user` - Run all tests
- `flask test user unit` - Run unit tests only
- `flask test user int` - Run integration tests only

## Configuration

### Environment Variables
The application uses the following configuration:
- `SQLALCHEMY_DATABASE_URI` - Database connection (default: SQLite)
- `SECRET_KEY` - Flask secret key for sessions
- Port 5000 is used for the web server (required for Replit)

### Default Configuration
Located in `App/default_config.py`:
- SQLite database: `sqlite:///temp-database.db`
- Secret key: Set in config (should be changed for production)

Custom configuration can be added via `App/custom_config.py` (takes precedence over default).

## Key Features
1. **Student Hour Tracking**: Students submit hours for approval
2. **Staff Review Workflow**: Staff can approve/deny requests with automatic hour logging
3. **Accolades System**: Students earn recognition based on hours (10, 25, 50 hour milestones)
4. **Leaderboard**: Ranking system based on approved hours with progress bars
5. **Activity History**: Track student progress over time with milestone tracking
6. **CLI Interface**: Comprehensive command-line tools
7. **Web Interface**: Modern responsive UI with purple theme
8. **Authentication**: JWT-based auth with cookie/header support, role-based access
9. **Admin Panel**: Flask-Admin integration for data management

## Web Pages

### Public Pages
- `/login` - User login page
- `/register` - User registration with Student/Staff role selection

### Student Pages (requires login as student)
- `/student/dashboard` - Dashboard with hours summary, recent activities, request form
- `/student/accolades` - Earned accolades and upcoming milestones
- `/student/confirmations` - Pending and confirmed hour requests
- `/student/hours` - Activity logs with status filters
- `/student/history` - Complete activity history with milestone markers
- `/student/leaderboard` - Student rankings by confirmed hours

### Staff Pages (requires login as staff)
- `/staff/dashboard` - Dashboard with pending requests overview
- `/staff/log-hours` - Form to log hours for students directly
- `/staff/requests` - View and manage pending student requests
- `/staff/request/<id>` - Detailed view of specific request
- `/staff/approve/<id>` - Approve a student request (POST)
- `/staff/deny/<id>` - Deny a student request (POST)
- `/staff/leaderboard` - Student rankings view

## Deployment
The application is configured for Replit deployment using:
- Deployment target: autoscale (scales based on traffic)
- Run command: `gunicorn -c gunicorn_config.py wsgi:app`
- Port: 5000 (automatically exposed by Replit)

## Development Notes
- Models use SQLAlchemy's polymorphic inheritance
- Password hashing via Werkzeug
- CORS enabled for cross-origin requests
- Gevent workers for async performance
- Flask-Migrate for database migrations
- Comprehensive test coverage with pytest

## User Preferences
- None specified yet

## Sample Data
The initialization creates:
- 5 sample students (alice, bob, charlie, diana, eve)
- 3 sample staff members (msmith, mjohnson, mlee)
- 4 sample hour requests
- 2 approved requests with logged hours
- 1 denied request
- 1 pending request
