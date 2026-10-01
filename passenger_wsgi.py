"""
Passenger entry point for cPanel "Setup Python App".

cPanel settings:
    Application root:          path to this folder (Equb_App_Backend)
    Application startup file:  passenger_wsgi.py
    Application Entry point:   application
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# manage.py loads .env but equb/wsgi.py does not, so load it here for Passenger.
# Variables set in the cPanel "Environment variables" section take precedence.
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env", override=False)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "equb.settings")

from equb.wsgi import application  # noqa: E402,F401
