# FilaQora

**FilaQora** is a web-based Customer Relationship Management (CRM) and customer management system developed using **Python, Flask, SQLAlchemy, PostgreSQL/SQLite, HTML5, CSS3, Bootstrap, and JavaScript**.

The application provides a centralized platform for managing customers, viewing business analytics, searching customer records, exporting customer data, managing user accounts, and accessing customer information through a secure REST API.

FilaQora is designed with a clean and responsive interface suitable for business management, academic projects, internships, and portfolio use.

---

## Features

### Customer Management

* Customer registration and management
* Add new customers
* View customer details
* Edit customer information
* Delete customer records
* Customer search
* Customer filtering
* Company information management
* Customer tag management
* Customer creation date tracking

### Dashboard & Analytics

* Real-time dashboard statistics
* Total customer count
* Customer growth analytics
* Top companies
* Customer tag analytics
* Recent customer information
* Business/customer overview
* Visual analytics and charts

### Authentication

* User registration/login system
* Secure password hashing
* Flask-Login authentication
* Session-based authentication
* Logout functionality
* Protected customer management pages
* User profile management
* Password change functionality

### REST API

* REST API for customer management
* Bearer token authentication
* Retrieve customers
* Retrieve individual customer
* Create customers
* Update customers
* Delete customers
* Customer search through API
* Pagination support
* JSON responses

### Data Export

* Export customer records as CSV
* Export customer records as Excel
* Excel generation using OpenPyXL
* Export filtering/search support

### Admin Management

* Administrator account
* Admin dashboard
* User management
* User registration overview
* Customer count per user
* Admin account configuration through environment variables
* Automatic admin database migration

### Database

* SQLite support for local development
* PostgreSQL support for production
* SQLAlchemy ORM
* Automatic database table creation
* Database connection pooling/pre-ping
* User/customer relationships
* Production-ready PostgreSQL configuration

### Additional Features

* Public landing page
* Public demo page
* API documentation page
* User profile page
* Responsive web interface
* Bootstrap-based UI
* Custom CSS styling
* JavaScript interactions
* Production deployment configuration for Render

---

# Tech Stack

## Frontend

* HTML5
* CSS3
* Bootstrap
* JavaScript
* Font Awesome / UI icons where applicable
* Jinja2 Templates

## Backend

* Python
* Flask
* Flask-Login
* Flask-SQLAlchemy
* SQLAlchemy
* Werkzeug

## Database

### Development

* SQLite

### Production

* PostgreSQL
* Psycopg2

## API

* REST API
* JSON
* Bearer Token Authentication

## Export

* CSV
* OpenPyXL
* Microsoft Excel (`.xlsx`)

## Deployment

* Gunicorn
* Render
* PostgreSQL

---

# Project Structure

```text
FilaQora/
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── Procfile
├── render.yaml
├── .env.example
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── main.js
│
└── templates/
    ├── base.html
    ├── index.html
    ├── dashboard.html
    ├── login.html
    ├── customers.html
    ├── customer_form.html
    ├── customer_detail.html
    ├── profile.html
    ├── admin.html
    ├── api_docs.html
    ├── export.html
    └── demo.html
```

---

# Database Design

FilaQora currently uses two primary database models:

## User Table

| Field           | Description              |
| --------------- | ------------------------ |
| `id`            | Unique user identifier   |
| `name`          | User name                |
| `email`         | Unique user email        |
| `password_hash` | Securely hashed password |
| `api_token`     | API authentication token |
| `is_admin`      | Administrator status     |
| `created_at`    | Account creation date    |

---

## Customer Table

| Field        | Description                             |
| ------------ | --------------------------------------- |
| `id`         | Unique customer identifier              |
| `user_id`    | Owner/user associated with the customer |
| `name`       | Customer name                           |
| `email`      | Customer email                          |
| `phone`      | Customer phone number                   |
| `company`    | Customer company                        |
| `tags`       | Customer tags                           |
| `created_at` | Customer creation date                  |

Each customer is associated with a user through a foreign-key relationship.

```text
User
 │
 ├── Customer
 ├── Customer
 ├── Customer
 └── Customer
```

The application uses SQLAlchemy relationships and cascade deletion to maintain customer ownership and data consistency.

---

# Application Workflow

The main application workflow is:

```text
User
  ↓
Login
  ↓
Dashboard
  ↓
Customer Management
  ↓
Add / Search / View Customers
  ↓
Edit Customer Information
  ↓
Export Customer Data
  ↓
Analytics & Reports
```

For API users:

```text
API Client
    ↓
Bearer Token
    ↓
Flask REST API
    ↓
Authentication
    ↓
Customer Query
    ↓
JSON Response
```

---

# Customer Management Workflow

1. User logs into FilaQora
2. User opens the Customer Management section
3. User adds customer information
4. Customer record is stored in the database
5. Customer appears in the customer list
6. User can search for the customer
7. User can view complete customer details
8. User can update customer information
9. User can delete customer records
10. Customer information can be exported as CSV or Excel

---

# Dashboard

The FilaQora dashboard provides an overview of customer data.

Dashboard functionality includes:

* Total customers
* Customer growth information
* Company statistics
* Customer tag statistics
* Recent customer records
* Business/customer analytics

The dashboard retrieves information directly from the database and presents it through the web interface.

---

# Authentication System

FilaQora uses **Flask-Login** for session-based authentication.

Passwords are not stored as plain text. Passwords are securely hashed using Werkzeug's password hashing functionality.

Authentication flow:

```text
Login Form
     ↓
Email + Password
     ↓
Database User Lookup
     ↓
Password Verification
     ↓
Flask-Login Session
     ↓
Authenticated Dashboard
```

Protected routes require the user to be authenticated before accessing customer information.

---

# REST API

FilaQora provides a REST API under:

```text
/api
```

The API uses Bearer Token authentication.

Example:

```http
Authorization: Bearer YOUR_API_TOKEN
```

---

## API Endpoints

### Get Customers

```http
GET /api/customers
```

Returns a paginated list of customers.

Optional query parameters include:

```text
q
page
per_page
```

Example:

```http
GET /api/customers?q=John&page=1&per_page=20
```

---

### Get Customer

```http
GET /api/customers/<id>
```

Returns a specific customer.

---

### Create Customer

```http
POST /api/customers
```

Example JSON:

```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "company": "Example Company",
    "tags": "client,priority"
}
```

---

### Update Customer

```http
PUT /api/customers/<id>
```

or:

```http
PATCH /api/customers/<id>
```

---

### Delete Customer

```http
DELETE /api/customers/<id>
```

---

# API Response Example

A customer response follows a JSON structure similar to:

```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "company": "Example Company",
    "tags": "client,priority",
    "created_at": "2026-09-25T10:30:00"
}
```

---

# Data Export

FilaQora supports exporting customer records.

## CSV Export

Customer information can be exported in CSV format.

Example:

```text
id,name,email,phone,company,tags,created_at
1,John Doe,john@example.com,9876543210,Example Company,client,...
```

## Excel Export

Customer records can also be exported as:

```text
filaqora-customers.xlsx
```

Excel files are generated using the **OpenPyXL** library.

---

# Admin System

FilaQora includes an administrator dashboard.

The administrator can view:

* Registered users
* User names
* User email addresses
* Administrator status
* Account creation dates
* Number of customers associated with each user

The administrator account is configured through environment variables.

Example:

```env
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-secure-password
ADMIN_NAME=FilaQora Administrator
```

For production deployments, administrator credentials should be stored securely as environment variables rather than hard-coded into the application.

---

# Database Configuration

FilaQora supports both SQLite and PostgreSQL.

## SQLite

When no `DATABASE_URL` is configured, the application automatically uses a local SQLite database:

```text
instance/filaqora.db
```

This is useful for:

* Local development
* Testing
* Academic demonstrations
* Small development environments

---

## PostgreSQL

For production deployments, FilaQora can use PostgreSQL through the `DATABASE_URL` environment variable.

Example:

```env
DATABASE_URL=postgresql://username:password@host/database
```

The application also handles the older:

```text
postgres://
```

connection format and converts it to the SQLAlchemy-compatible:

```text
postgresql://
```

format.

---

# Environment Variables

Create a `.env` file for local development if required.

Example:

```env
SECRET_KEY=your-secret-key

DATABASE_URL=

ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-secure-password
ADMIN_NAME=FilaQora Administrator
```

### Important

Do not commit real passwords, API tokens, secret keys, or production database credentials to GitHub.

Use:

```text
.env
```

for local secrets and environment variables.

The project includes:

```text
.env.example
```

as a configuration reference.

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/tarunumesh01/FilaQora.git
```

Move into the project directory:

```bash
cd FilaQora
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The main dependencies include:

```text
Flask
Flask-Login
Flask-SQLAlchemy
SQLAlchemy
Werkzeug
psycopg2-binary
Gunicorn
python-dotenv
OpenPyXL
```

---

# Run the Application

Start the Flask application with:

```bash
python app.py
```

The application runs on:

```text
http://127.0.0.1:5000/
```

Open the address in your browser.

---

# Production Deployment

FilaQora includes deployment configuration for **Render**.

The project contains:

```text
render.yaml
```

and:

```text
Procfile
```

The production application uses Gunicorn:

```bash
gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2
```

The Render configuration also provisions a PostgreSQL database for production use.

---

# Production Architecture

```text
                    ┌───────────────────┐
                    │      Browser      │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   Flask Web App   │
                    │                   │
                    │ Authentication    │
                    │ Customer CRM       │
                    │ Dashboard         │
                    │ REST API          │
                    │ Export System     │
                    └─────────┬─────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
             ┌──────────────┐    ┌──────────────┐
             │ PostgreSQL   │    │ REST API     │
             │ Production   │    │ Clients      │
             └──────────────┘    └──────────────┘
```

For local development:

```text
Flask
  ↓
SQLAlchemy
  ↓
SQLite
```

For production:

```text
Flask
  ↓
SQLAlchemy
  ↓
PostgreSQL
```

---

# User Interface

FilaQora includes a responsive web interface with:

* Navigation bar
* Dashboard cards
* Customer tables
* Customer forms
* Search interfaces
* Customer detail pages
* Profile management
* Admin dashboard
* API documentation
* Export interface
* Responsive layouts
* Status and notification messages

The frontend uses server-rendered **Jinja2 templates** together with CSS and JavaScript.

---

# Main Pages

| Page              | Purpose                  |
| ----------------- | ------------------------ |
| `/`               | Public landing page      |
| `/demo`           | Public demo page         |
| `/login`          | User authentication      |
| `/dashboard`      | Main analytics dashboard |
| `/customers`      | Customer management      |
| `/customers/new`  | Add customer             |
| `/customers/<id>` | Customer details/edit    |
| `/export`         | Customer data export     |
| `/api-docs`       | REST API documentation   |
| `/profile`        | User profile management  |
| `/admin`          | Administrator dashboard  |

---

# Security

FilaQora implements several security-related mechanisms:

* Password hashing
* Flask-Login authentication
* Protected application routes
* User-specific customer access
* Bearer-token API authentication
* Environment-based secrets
* Unique user email addresses
* Unique API tokens
* Admin access controls

Customer queries are scoped to the authenticated user so that users access their own customer records through the application.

---

# Requirements

Recommended environment:

```text
Python 3.12+
```

The project dependencies are defined in:

```text
requirements.txt
```

Current core dependencies include:

```text
Flask==3.1.0
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.36
Werkzeug==3.1.3
psycopg2-binary==2.9.10
gunicorn==23.0.0
python-dotenv==1.0.1
openpyxl==3.1.5
```

---

# Future Enhancements

Possible future improvements include:

* Advanced role-based access control
* Staff accounts
* Customer activity history
* Advanced analytics
* Automated reports
* PDF customer reports
* Email notifications
* SMS notifications
* Import customers from CSV/Excel
* Advanced customer filtering
* Audit logs
* Customer communication history
* API rate limiting
* API key management interface
* Advanced PostgreSQL reporting
* Cloud file storage
* Automated database backups
* Two-factor authentication

---

# Learning Outcomes

This project demonstrates practical knowledge of:

* Python programming
* Flask web application development
* MVC-style application organization
* SQLAlchemy ORM
* SQLite database development
* PostgreSQL integration
* HTML5
* CSS3
* JavaScript
* Jinja2 templating
* User authentication
* Password hashing
* REST API development
* Bearer token authentication
* JSON data handling
* CSV export
* Excel file generation
* Database relationships
* Environment variable management
* Git and GitHub
* Production deployment
* Gunicorn
* Render deployment

---

# Project Information

**Project Name:** FilaQora

**Project Type:** Customer Relationship Management / Customer Management System

**Backend:** Python + Flask

**Database:** SQLite / PostgreSQL

**Frontend:** HTML5 + CSS3 + JavaScript

**ORM:** SQLAlchemy

**Authentication:** Flask-Login

**API:** REST API with Bearer Token Authentication

**Deployment:** Render + Gunicorn

**Export:** CSV + Excel

---

# Author

**Student Name:** Tarun U

**Email:** [tarunumesh23@gmail.com](mailto:tarunumesh23@gmail.com)

**Course:** BCA

**Project:** FilaQora

**Technologies:**

```text
Python
Flask
SQLAlchemy
PostgreSQL
SQLite
HTML5
CSS3
JavaScript
REST API
Bootstrap
Git
GitHub
```

---

# GitHub

Repository:

https://github.com/tarunumesh01/FilaQora

---

# License

This project is developed for **educational, academic, internship, and portfolio purposes**.

See the `LICENSE` file for additional license information.

---

# FilaQora

> **Manage customers. Understand your data. Build better relationships.**

FilaQora combines customer management, analytics, data export, authentication, administration, and REST API functionality into a single Flask-based web application.
