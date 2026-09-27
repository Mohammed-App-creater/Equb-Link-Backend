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
  - Password reset by SMS code: `password-reset/request/` + `password-reset/confirm/` (also under `api/owner/`). Codes are HMAC-hashed, 10 min TTL, 5 attempts, 60 s resend cooldown; confirm revokes all auth tokens. SMS goes through `user/sms.py`; `SMS_PROVIDER=console` (dev, prints the code and returns `debug_code` when DEBUG) or `afromessage` (needs `AFROMESSAGE_TOKEN`, optional `AFROMESSAGE_IDENTIFIER_ID`/`AFROMESSAGE_SENDER_NAME`).
- `equbApp`: EqubType, EqubCategory, OwnerBankAccount, Equb, EqubMember, Payment, LotteryWinner, Notification (has `is_pinned`), SupportTicket, AppConfig. Holds the customer and mobile endpoints and Chapa (`chapa/initialize/`, `chapa/verify/<tx_ref>/`, `chapa/callback/`, `payment-success/`). Customer notification actions: `notifications/read/`, `read-all/`, `clear-all/`, `<id>/toggle-pin/`. Customer support tickets: `support/tickets/` (GET own, POST create); `admin/support-tickets/` is admin-only.
- `owner_panel`: owner API mounted at both `/api/owner/` and `/owner/`. Models: AuditLog, LotteryRound. Endpoints for approving/rejecting members and payments, round draw and payout, export (pandas), reports and activity. `equbs/<id>/payments/record/` lets the owner record an off-app payment (created as completed). The admin panel loads its profile from `api/owner/profile/` (defined in the `user` app).
- `advert`: Advert, Testimonial, Feedback, FAQ

## Commands (Windows, from this folder)
- Activate venv: `myenv\Scripts\activate`
- Run: `python manage.py runserver`
- Migrations: `python manage.py makemigrations && python manage.py migrate`. Create them locally and commit them.
- Tests: `python manage.py test equbApp user owner_panel advert` — the app labels are required. Plain `manage.py test` finds 0 tests because `api/` is not a package, so discovery never descends into it.
- API docs: http://localhost:8000/api/schema/docs/ (Swagger) and `/api/schema/redoc/`

## Deploy
Pushing to `main` triggers `.github/workflows/deploy.yml`, which SSHes to the VPS and runs `/root/equb/deploy.sh` (see `.scripts/deploy.sh`): git pull, pip install, collectstatic, migrate, then restart gunicorn and nginx. Production API: `https://api.equb.equblinktrading.com/`.

## Permissions & routing rules
- Platform-admin API lives under **`api/admin/...`** (not `admin/...`: the Django admin site is mounted at `/admin/` and its catch-all swallows anything below it).
- Use `user.permissions.IsAdminUser` (checks `is_admin`/superuser) for platform-admin views, never DRF's `IsAdminUser` (checks `is_staff`, which equb owners also have for the Django admin site).
- Owner views use `owner_panel.permissions.IsEqubOwner` and must scope every lookup by `owner=request.user` with `get_object_or_404`.
- DRF has no default permission class here, so a view without `@permission_classes` is **public**. Only signup/login/password-reset, public catalog/FAQ, and the Chapa callback should be.
- Lottery draws use a random `secrets` seed recorded on the round; the winner is reproducible from the seed afterwards but not predictable before.
- Every user-uploaded file goes through `equbApp.uploads.validate_image_upload()` (type, size, real image) before saving; models use random upload paths. Never save `request.FILES[...]` directly.
- `/media/` is served by `equbApp.media_views.serve_media`; `receipt_images/` requires the payer/owner/admin or a signed URL (`signed_media_url`). The web server must not serve `/media/receipt_images/` itself.
- Auth tokens expire after `AUTH_TOKEN_TTL_DAYS` (`user.authentication.ExpiringTokenAuthentication`); `POST /logout/` revokes. Login/signup/reset are rate-limited (`user/throttles.py`, rates in settings).
- Self-registration (`/signup`, `/signup/customer/`) is customer-only. `UserSerializer` has an explicit field list; never expose `password`/permissions.
- `EqubSerializer` only includes `payout_bank_accounts` when the view passes `include_payout_accounts=True` (members/owner/admin/joining); `UserPublicSerializer` only includes `phone` with `include_member_phones=True`.
- `notify_admins(message, notif_type, equb=...)` reaches platform admins plus that equb's owner only.
- Run `pip-audit` / `npm audit` before releases; keep Django/DRF/Pillow current.

## Config & deploy notes
- `DEBUG` and `ALLOWED_HOSTS` come from `.env`. `DEBUG` defaults to **False**; set `DEBUG=True` locally or Django will not serve `/media/` and `/static/` itself. `ALLOWED_HOSTS` is comma-separated and defaults to the production host plus localhost.
- Migrations are committed. **Never run `makemigrations` on the server.** Generate locally, commit, and `deploy.sh` runs `migrate`. A model change and its migration go in the same commit.
- The GitHub workflow pulls `main` and then runs `.scripts/deploy.sh` from the repo, so edits to that script take effect on the next deploy.
- `STATIC_URL = "/equb/static/"` matches the Nginx config; don't change it casually. With `DEBUG=False`, Nginx must serve `/media/` too.
- Env vars in `.env`: `DJANGO_SECRET_KEY`, `CHAPA_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`. `CHAPA_BASE_URL` is unused because the Chapa host is hardcoded at the call sites.
