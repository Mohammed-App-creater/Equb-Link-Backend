# Equb_App_Backend (Django) — the active backend

Full map: `BACKEND_MAP.md`. Endpoint list: `API_ENDPOINTS.md`.

## Stack
Django 5.2, DRF 3.16, drf-spectacular, django-cors-headers, django-filter, django-cleanup, Pillow, pandas/openpyxl (Excel export), requests (Chapa). The admin UI uses Jazzmin and django-admin-interface.
- DB: SQLite (`db.sqlite3`). The MySQL config in `equb/settings.py` is commented out.
- Auth: DRF `TokenAuthentication`. Custom user model is `user.Account`, keyed on phone number. The profile models are `Admin`, `Customer` and `EqubAdmin`.
- Pagination: `PageNumberPagination`, `PAGE_SIZE = 6`. Lists return `{count, next, previous, results}`.
- Project package: `equb/` (settings, root urls). Apps live in `api/`, which is added to `sys.path`, so import them as `from equbApp...`, not `from api.equbApp...`.

## Apps
- `user`: signup, login, me, profile update, change password, admin creation
- `equbApp`: EqubType, EqubCategory, OwnerBankAccount, Equb, EqubMember, Payment, LotteryWinner, Notification, SupportTicket, AppConfig. Holds the customer and mobile endpoints and Chapa (`chapa/initialize/`, `chapa/verify/<tx_ref>/`, `chapa/callback/`, `payment-success/`).
- `owner_panel`: owner API mounted at both `/api/owner/` and `/owner/`. Models: AuditLog, LotteryRound. Endpoints for approving/rejecting members and payments, round draw and payout, export (pandas), reports and activity.
- `advert`: Advert, Testimonial, Feedback, FAQ

## Commands (Windows, from this folder)
- Activate venv: `myenv\Scripts\activate`
- Run: `python manage.py runserver`
- Migrations: `python manage.py makemigrations && python manage.py migrate`. Create them locally and commit them.
- Tests: `python manage.py test`
- API docs: http://localhost:8000/api/schema/docs/ (Swagger) and `/api/schema/redoc/`

## Deploy
Pushing to `main` triggers `.github/workflows/deploy.yml`, which SSHes to the VPS and runs `/root/equb/deploy.sh` (see `.scripts/deploy.sh`): git pull, pip install, collectstatic, migrate, then restart gunicorn and nginx. Production API: `https://api.equb.equblinktrading.com/`.

## Config & deploy notes
- `DEBUG` and `ALLOWED_HOSTS` come from `.env`. `DEBUG` defaults to **False**; set `DEBUG=True` locally or Django will not serve `/media/` and `/static/` itself. `ALLOWED_HOSTS` is comma-separated and defaults to the production host plus localhost.
- Migrations are committed. **Never run `makemigrations` on the server.** Generate locally, commit, and `deploy.sh` runs `migrate`. A model change and its migration go in the same commit.
- The GitHub workflow pulls `main` and then runs `.scripts/deploy.sh` from the repo, so edits to that script take effect on the next deploy.
- `STATIC_URL = "/equb/static/"` matches the Nginx config; don't change it casually. With `DEBUG=False`, Nginx must serve `/media/` too.
- Env vars in `.env`: `DJANGO_SECRET_KEY`, `CHAPA_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`. `CHAPA_BASE_URL` is unused because the Chapa host is hardcoded at the call sites.
