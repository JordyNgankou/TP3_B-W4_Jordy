from collections import defaultdict
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


# ----------------------
# Dictionary Helper
# ----------------------

def merge_errors(*dicts):
    merged = defaultdict(list)
    for d in dicts:
        for key, value in d.items():
            merged[key].extend(value)
    return dict(merged)


# ----------------------
# Refresh Cookie Helper
# ----------------------

REFRESH_COOKIE_NAME = "refreshtoken"


def delete_refresh_cookie(response):
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
    )

def get_refresh_cookie(request):
    return request.COOKIES.get(REFRESH_COOKIE_NAME)

def set_refresh_cookie(response, refresh_token, cookie_path):
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=str(refresh_token),
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path=cookie_path,
    )


# ----------------------
# Refresh Token Helper
# ----------------------

def blacklist_all_refresh_tokens(user):
    BlacklistedToken.objects.bulk_create(
        [
            BlacklistedToken(token=token)
            for token in OutstandingToken.objects.filter(user=user)
        ],
        ignore_conflicts=True,
    )

def blacklist_refresh_token_from_cookie(request):
    refresh_cookie = get_refresh_cookie(request)
    if refresh_cookie:
        try:
            refresh_token = RefreshToken(refresh_cookie)
            refresh_token.blacklist()
        except Exception:
            pass  # Si déjà invalidé ou expiré
