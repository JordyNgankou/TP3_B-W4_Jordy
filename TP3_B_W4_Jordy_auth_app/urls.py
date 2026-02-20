from django.urls import path

from .views import (
  CustomTokenObtainPairView,
  CustomTokenRefreshView,
  LogoutView,
  MeView,
  MePasswordView,
  RegisterView,
)

urlpatterns = [
  path('token/', CustomTokenObtainPairView.as_view()),
  path('token/delete/', LogoutView.as_view()),
  path('token/refresh/', CustomTokenRefreshView.as_view()),

  path('me/', MeView.as_view(),),
  path('me/password/', MePasswordView.as_view()),
  path('register/', RegisterView.as_view()),
]
