# BCDC Cafe Management System

BCDC Cafe Management System is a Django web application for day-to-day cafe operations. Customers can browse the menu, create an account, and place orders. Cafe administrators can manage tables, menu inventory, purchases, staff, expenses, and bills from the admin area.

## Features

- Customer registration, login, profile, and order history
- Cafe menu with item details and available stock
- Table and order management, including bill printing and settlement
- Inventory tracking with stock updates when customer orders are placed
- Admin pages for tables, items, purchases, staff, and expenses
- SQLite for local development and PostgreSQL support through `DATABASE_URL`
- Static asset serving with WhiteNoise for deployment

## Technology

- Python 3.12 or newer
- Django 6.1
- SQLite (local default) or PostgreSQL
- WhiteNoise for static files

## Run locally

Run these commands from the project root. Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` instead. Then apply migrations and start the development server:

```bash
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Register a customer account to try the customer flow. The administrator registration and login pages are available from the application.

## Configuration

The following environment variables are available:

| Variable | Purpose | Local behavior |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django signing key | Uses a development fallback if unset; set a private, strong value for deployment |
| `DJANGO_DEBUG` | Enables Django debug mode | Defaults to `true` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names accepted by Django | Defaults to `localhost,127.0.0.1,testserver` |
| `DATABASE_URL` | PostgreSQL connection URL | If unset, uses `db.sqlite3` in the project root |
| `RENDER_EXTERNAL_HOSTNAME` | Render service hostname | Adds the hostname to allowed hosts and trusted HTTPS origins when set |

When `DJANGO_DEBUG=false`, provide `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS`. Secure cookies, HTTPS redirects, and HSTS are enabled in this mode, so the application should be served over HTTPS. If deploying to Render, configure a persistent PostgreSQL database and set `DATABASE_URL`, set `DJANGO_DEBUG=false`, and provide a strong `DJANGO_SECRET_KEY`. Render supplies `RENDER_EXTERNAL_HOSTNAME` for its web service.

## Deploy on Render

Create a Render web service connected to this repository and configure:

- **Build command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start command:** `gunicorn cafe.wsgi:application`
- **Environment:** `DJANGO_DEBUG=false`, a generated `DJANGO_SECRET_KEY`, and `DATABASE_URL` from a persistent PostgreSQL database

Render sets `RENDER_EXTERNAL_HOSTNAME` for the service. If your deployment host does not provide it, add the hostname to `DJANGO_ALLOWED_HOSTS`.

## Useful commands

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
```

## Project structure

- `cafe/` — Django project settings and URL configuration
- `cafe_app/` — application models, views, templates, static assets, migrations, and tests
- `requirements.txt` — Python dependencies
- `manage.py` — Django management commands
- `Cafe_Management_System_Project_Report.docx` — project report

The local SQLite database, virtual environment, IDE settings, and generated static files are excluded from Git.
