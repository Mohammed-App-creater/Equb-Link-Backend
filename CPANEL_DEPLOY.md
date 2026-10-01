# Deploying on cPanel (Setup Python App)

The entry point is `passenger_wsgi.py`. It loads `.env` and starts Django. Static files are served by WhiteNoise, and media files are served by the `serve_media` view, so Apache needs no extra config.

## 1. Upload the code
Clone or upload this repo to a folder outside `public_html`, for example `~/equb_backend`. Do not upload `myenv/`, `db.sqlite3`, or `static/`.

## 2. Create the app
In cPanel, open **Setup Python App** and click **Create Application**.

| Field | Value |
|---|---|
| Python version | 3.10 or newer (Django 5.2 requires it) |
| Application root | `equb_backend` (the folder from step 1) |
| Application URL | the API domain, e.g. `api.equb.equblinktrading.com` (mount at the root `/`, not a sub-path) |
| Application startup file | `passenger_wsgi.py` |
| Application Entry point | `application` |

Click **Create**. If `passenger_wsgi.py` did not exist yet, cPanel writes a stub in its place. Make sure the file contains the repo's version, which starts with `"""Passenger entry point for cPanel`.

## 3. Create `.env` in the application root
Copy `.env.example` to `.env` and set at least:

```
DEBUG=False
DJANGO_SECRET_KEY=<50+ random characters>
ALLOWED_HOSTS=api.equb.equblinktrading.com
CORS_ALLOWED_ORIGINS=https://equb-admin-panal.vercel.app
CHAPA_SECRET_KEY=...
```

Generate a secret key with this command:
`python -c "import secrets; print(secrets.token_urlsafe(64))"`

With `DEBUG=False`, the app refuses to start if the key is shorter than 50 characters. Use one `KEY=value` per line, with no spaces around `=`.

You can also set these variables in the app's **Environment variables** section in cPanel. Values set there override `.env`.

## 4. Install and initialise
At the top of the app page, cPanel shows a command like `source /home/<user>/virtualenv/equb_backend/3.x/bin/activate && cd /home/<user>/equb_backend`. Run it in **Terminal**, then run:

```
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo --password '<strong password>'   # first deploy only
```

`seed_demo` creates the accounts and data used in the submission documents. Every demo account uses the password you pass.

| Role | Phone to type | Where |
|---|---|---|
| Platform admin | `0911000000` | `/admin/` and the admin panel |
| Equb owner | `0911223344` | Admin panel |
| Customer, Abebe Kebede (member of "Monthly 10K") | `911234567` | Mobile app |
| Customer, Sara Tesfaye (no equb, for testing joining) | `922345678` | Mobile app |

The command also creates:
- 29 member accounts, `+251911001001` to `+251911001029`, with the same password
- 6 categories, each with an image
- the five frequencies (Daily to Yearly)
- CBE, Telebirr and Awash payout accounts
- 7 equbs:
  - **Monthly 10K**: ETB 1,000 x 10, full. Rounds 1 and 2 are drawn, and round 3 is in progress with 2 payments waiting for approval.
  - **Quarterly Business Equb**: round 2 is fully paid, so the owner can run a draw.
  - **Daily Drivers 500**, **Weekly Office Savings**, **Student Weekly 200**, **Yearly Family Equb**: open for joining. Two of them have a pending join request.
  - **Merchants Daily 1K**: a draft.
- winners with draw seeds and payouts
- notifications, support tickets, adverts and testimonials
- FAQs and audit-log entries
- app-config 1.2.0

You can run it again safely. Add `--reset-passwords` to change the password on accounts that already exist.

## 5. Restart
Click **Restart** on the app page, or run `touch tmp/restart.txt` in the app root.

To check that it works, open these URLs:
- `https://<domain>/app-config` should return JSON.
- `https://<domain>/admin/` should show the styled admin login.

## Updating
```
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

## Troubleshooting
- **`RecursionError` with `imp.load_source('wsgi', 'passenger_wsgi.py')` in the log:** cPanel replaced `passenger_wsgi.py` with its own stub, which loads itself in a loop. This happens if the app is created before the code is uploaded. Replace the file with the repo's `passenger_wsgi.py` (`git checkout passenger_wsgi.py`), then restart.
- **Errors:** the error log is `stderr.log` in the app root. You can also check cPanel under **Metrics → Errors**.
- **"DJANGO_SECRET_KEY must be at least 50 random characters":** `.env` was not found or not parsed. Check that it sits next to `passenger_wsgi.py`.
- **400 Bad Request:** the domain is missing from `ALLOWED_HOSTS`.
- **Admin page without styling:** run `collectstatic`, then restart.
- **"attempt to write a readonly database":** the app root and `db.sqlite3` must be writable by your cPanel user.
