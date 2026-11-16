# BCDC Cafe Management System

A Django web application for managing a cafe menu, inventory, tables, orders, billing, staff, purchases, and expenses. It includes customer registration and login, a menu with stock availability, and an admin dashboard for cafe operations.

## Requirements

- Python 3.12 or newer
- Django 6.1

The project uses SQLite by default, so no separate database server is needed for local development.

## Run locally

From the project root, create and activate a virtual environment, then install Django:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install "Django>=6.1,<6.2"
```

On macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install "Django>=6.1,<6.2"
```

Apply database migrations and start the development server:

```bash
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser. Register an account through the app to try the customer flow. Use the admin registration page to create an application admin account.

## Useful commands

```bash
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

## Configuration

The app reads these optional environment variables:

| Variable | Purpose | Local default |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django signing key | Development-only fallback in settings |
| `DJANGO_DEBUG` | Enables debug mode | `true` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed host names | `localhost,127.0.0.1,testserver` |

Before deployment, set a strong `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=false`, and set `DJANGO_ALLOWED_HOSTS` to the deployed host names. The settings enable secure cookies, HTTPS redirects, and HSTS when debug mode is disabled; serve the site over HTTPS in that configuration.

## Project layout

- `cafe/` — Django project settings and URL configuration
- `cafe_app/` — application models, views, templates, static images, migrations, and tests
- `manage.py` — Django management commands
- `Cafe_Management_System_Project_Report.docx` — project report

The local SQLite database, virtual environment, IDE settings, and generated files are excluded from Git.
