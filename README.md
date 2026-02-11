# FJ Finance - Personal Finance Tracker

A comprehensive financial management tool built with Django.

## Features
- **Modern Dashboard**: Overview of monthly income, expenses, and savings.
- **Transaction Management**: Add, edit, delete, and track income/expenses.
- **Budgeting**: Set monthly budgets by category and receive alerts.
- **Reporting**: Monthly financial Standing reports with currency filtering.
- **Receipt Storage**: Upload and store receipts for transactions.
- **Bank Import**: Bulk upload transactions via CSV.
- **Anomaly Detection**: Automatically flag unusual spending patterns.
- **Premium UI**: Glassmorphism design with dark mode and animations.

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL (Local or Cloud)

### Setup
1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env`:
   ```ini
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgres://user:password@localhost:5432/db_name
   EMAIL_HOST_USER=your-sendgrid-username
   EMAIL_HOST_PASSWORD=your-sendgrid-key
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Start the server:
   ```bash
   python manage.py runserver
   ```

## Tech Stack
- **Framework**: Django
- **Authentication**: Django-Allauth (Google OAuth support)
- **Styling**: Vanilla CSS (Premium Glassmorphism), Bootstrap 5
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Email**: SendGrid / SMTP
