from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)

admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)
