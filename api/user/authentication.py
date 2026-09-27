"""
Token authentication with an expiry.

DRF's TokenAuthentication issues one permanent token per user. Here a token
older than settings.AUTH_TOKEN_TTL_DAYS is rejected (401 "Token expired") so
a leaked token cannot be used forever; login issues a fresh one.
"""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token


def token_is_expired(token: Token) -> bool:
    ttl_days = getattr(settings, "AUTH_TOKEN_TTL_DAYS", 30)
    if not ttl_days:
        return False
    return token.created < timezone.now() - timedelta(days=ttl_days)


def issue_token(user) -> Token:
    """Replace any existing token for the user with a fresh one."""
    Token.objects.filter(user=user).delete()
    return Token.objects.create(user=user)


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if token_is_expired(token):
            token.delete()
            raise exceptions.AuthenticationFailed("Token expired. Please sign in again.")
        return user, token
