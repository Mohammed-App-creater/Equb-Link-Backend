"""
Per-endpoint rate limits for the unauthenticated entry points (brute-force,
enumeration and SMS-flooding protection). Rates live in
settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].
"""
from rest_framework.throttling import AnonRateThrottle


class LoginThrottle(AnonRateThrottle):
    scope = "login"


class SignupThrottle(AnonRateThrottle):
    scope = "signup"


class PasswordResetRequestThrottle(AnonRateThrottle):
    scope = "password_reset_request"


class PasswordResetConfirmThrottle(AnonRateThrottle):
    scope = "password_reset_confirm"
