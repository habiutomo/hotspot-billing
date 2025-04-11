
# Hotspot Billing System

A Flask-based web application for managing internet hotspot customers, billing, and PPP connections.

## Features

- User Authentication (Admin/Staff login)
- Customer Management
- PPP Connection Monitoring
- Billing Management
- Revenue Reports & Analytics
- Responsive Dashboard

## Tech Stack

- Python 3.11
- Flask Framework
- Flask-Login for authentication
- Gunicorn WSGI server
- Bootstrap 5 for UI

## Getting Started

1. Click the "Run" button to start the server
2. Access the application at the provided URL
3. Login with default credentials:
   - Username: admin
   - Password: admin123

## API Endpoints

### Customers
- GET `/api/customers` - List all customers
- GET `/api/customers/<id>` - Get customer details
- POST `/api/customers` - Create new customer
- PUT `/api/customers/<id>` - Update customer
- DELETE `/api/customers/<id>` - Delete customer

### Billing
- GET `/api/billings` - List all billing records
- POST `/api/billings` - Create new billing record
- PUT `/api/billings/<id>` - Update billing status

### Reports
- GET `/api/reports/revenue` - Get revenue statistics
- GET `/api/reports/connections` - Get connection statistics
- GET `/api/reports/billing_status` - Get billing status overview
