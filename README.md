# Project10-NetTool

Project10-NetTool is a simple Flask web application prototype for a network engineer. The app stores and displays network device information and supports user login with role-based access control.

## Features

- User login and logout
- Admin and Viewer roles
- Admin can add, edit, delete, and view devices
- Viewer can search and view devices only
- Device list with search functionality
- Input validation for IP address, network mask, and gateway
- Flash messages for success and error feedback
- Parameterized SQL queries for security
- MySQL database support using `mysql-connector-python`

## Technology Stack

- Python
- Flask
- MySQL
- mysql-connector-python
- Werkzeug for password hashing
- HTML templates and CSS
- dotenv for environment variables

## Setup Instructions

1. Clone or copy the repository into a local folder.
2. Create a virtual environment and activate it.
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - Or use `.venv` if preferred: `python -m venv .venv` then `.venv\Scripts\activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Create a `.env` file from `.env.example` and update the database credentials.
   - Set `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` for your local MySQL server.
   - Set a strong `SECRET_KEY` in `.env` before running the app.
   - Keep `.env` private and do not commit it to GitHub.
   - For local development, you may keep `FLASK_DEBUG=1`; disable it for production.
5. Create the MySQL database and tables:
   - Run the SQL script `schema.sql` in your MySQL environment.
6. Start the Flask app:
   - `python app.py`
7. Open `http://127.0.0.1:5000` in a browser.

## Database Setup

The app uses a MySQL database named `nettool_db`.

1. Make sure MySQL server is running.
2. Run `schema.sql` to create the database, tables, sample roles, users, device types, and sample devices.
3. The sample users are created with hashed passwords.

## Default Login Credentials

> Note: Debug mode is enabled by default for local testing via `FLASK_DEBUG=1`. Disable debug mode in production.


- Admin user:
  - Username: `admin`
  - Password: `Admin123!`
- Viewer user:
  - Username: `viewer`
  - Password: `Viewer123!`

## Admin vs Viewer Role

- Admin
  - Add new devices
  - Edit existing devices
  - Delete devices
  - View all devices
- Viewer
  - Search devices
  - View device details
  - Cannot access add, edit, or delete pages

## Security Notes

- Passwords are stored as Werkzeug hashes, not plain text.
- Database credentials are not stored in `app.py`; use environment variables.
- `SECRET_KEY` must be configured in `.env`; do not use the default placeholder for production.
- SQL queries use parameterized queries to prevent SQL injection.
- Session data is used for login state.

## Testing Checklist

- [ ] Login with admin credentials
- [ ] Login with viewer credentials
- [ ] Verify admin can add a device
- [ ] Verify admin can edit a device
- [ ] Verify admin can delete a device
- [ ] Verify viewer cannot see admin buttons
- [ ] Verify viewer cannot access admin URLs
- [ ] Search devices using the search form
- [ ] Submit invalid IP address and confirm validation message
- [ ] Confirm logout returns to login page
- [ ] Confirm hashed passwords are stored in the database

## Screenshots to capture for report

1. VS Code project structure
2. MySQL database tables
3. Login page
4. Invalid login error
5. Admin dashboard
6. Viewer dashboard
7. Admin device list with buttons
8. Viewer read-only device list
9. Add device form
10. Device added successfully
11. Edit device form
12. Delete device
13. Access denied for viewer
14. Invalid IP validation
15. Hashed password in database
16. GitHub repository page
