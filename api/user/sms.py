"""
Outbound SMS used for password-reset codes.

Provider is chosen with the SMS_PROVIDER setting (env var):
  - "console"     : development — prints/logs the message instead of sending
  - "afromessage" : AfroMessage (https://afromessage.com) HTTP API; needs
                    AFROMESSAGE_TOKEN (+ optional AFROMESSAGE_IDENTIFIER_ID,
                    AFROMESSAGE_SENDER_NAME)
Add another provider by adding a `_send_<name>` function and a branch below.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

AFROMESSAGE_SEND_URL = "https://api.afromessage.com/api/send"


class SmsDeliveryError(Exception):
    """Raised when the SMS could not be handed to the provider."""


def send_sms(phone: str, message: str) -> None:
    provider = (getattr(settings, "SMS_PROVIDER", "console") or "console").strip().lower()

    if provider == "console":
        logger.info("SMS (console provider) to %s: %s", phone, message)
        print(f"[SMS -> {phone}] {message}")
        return

    if provider == "afromessage":
        _send_afromessage(phone, message)
        return

    raise SmsDeliveryError(f"Unknown SMS_PROVIDER '{provider}'")


def _send_afromessage(phone: str, message: str) -> None:
    token = getattr(settings, "AFROMESSAGE_TOKEN", "")
    if not token:
        raise SmsDeliveryError("AFROMESSAGE_TOKEN is not configured")

    payload = {"to": phone, "message": message}
    identifier = getattr(settings, "AFROMESSAGE_IDENTIFIER_ID", "")
    sender = getattr(settings, "AFROMESSAGE_SENDER_NAME", "")
    if identifier:
        payload["from"] = identifier
    if sender:
        payload["sender"] = sender

    try:
        response = requests.post(
            AFROMESSAGE_SEND_URL,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        data = response.json() if response.content else {}
    except (requests.RequestException, ValueError) as exc:
        logger.warning("AfroMessage request failed for %s: %s", phone, exc)
        raise SmsDeliveryError(str(exc)) from exc

    if not response.ok or str(data.get("acknowledge", "")).lower() != "success":
        detail = data.get("response") or f"HTTP {response.status_code}"
        logger.warning("AfroMessage rejected SMS to %s: %s", phone, detail)
        raise SmsDeliveryError(str(detail))
