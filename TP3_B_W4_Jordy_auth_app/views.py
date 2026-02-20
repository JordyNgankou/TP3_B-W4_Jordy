from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.views import APIView

from .helpers import (
    blacklist_all_refresh_tokens,
    blacklist_refresh_token_from_cookie,
    delete_refresh_cookie,
    get_refresh_cookie,
    merge_errors,
    set_refresh_cookie
)

from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
    UserDeleteSerializer,
    UserPasswordSerializer
)

"""
Précisions Steve :

Il existe la vue rest_framework_simplejwt.views.TokenObtainPairView,
qui s'attend à recevoir (par défaut) en POST : { "username": "...", "password": "..." }
et qui retourne (lorsque ces information sont valides),
le token d'accès et le token de refresh : { "access": "...", "refresh": "..." }

Il existe aussi rest_framework_simplejwt.views.TokenRefreshView,
qui s'attend à recevoir en POST : { "refresh" : "..." }
et qui retourne (lorsque le token de refresh est valide),
un nouveau token d'accès : { "access": "..." }

Utiliser directement ces vues est une bonne idée lorsque vous pouvez stocker ces tokens
de façon sécurisée sur le périphérique "client".
Par exemple, stocker dans le SecureStore via une application mobile.

Mais lorsque vous utiliser votre API avec un site web, il n'y a pas de "storage" sécurisé
de disponible : le localStorage n'est pas sécurisé.
On veut également éviter que le token "refresh" soit disponible en lecture
via le JavaScript : sinon on s'expose à la faille XSS.

Il faut donc en web, plutôt utiliser un cookie HttpOnly qui ne peut pas être lu
par JavaScript : uniquement par l'API.

C'est pourquoi, nous devons créer des vues personnalisées :
CustomTokenObtainPairView et CustomTokenRefreshView

Pour la démo, j'en profite également pour retourner l'utilisateur connecté.
Cela me permet de récupérer l'utilisateur directement après la connexion ("/auth/token/")
et après la réactualisation du token d'accès ("/auth/token/refresh/").

Ça évite d'appeler "/auth/me/" pour récupérer les informations de l'utilisateur connecté.
"""


class CustomTokenObtainPairView(APIView):
    http_method_names = ['post']

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        response = Response(serializer.validated_data)
        set_refresh_cookie(response, str(serializer.refresh_token), "/auth/token/")
        return response


class CustomTokenRefreshView(APIView):
    http_method_names = ['post']

    def post(self, request):
        refresh_cookie = get_refresh_cookie(request)
        if not refresh_cookie:
            return Response({"detail": "No refresh cookie"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh_token = RefreshToken(refresh_cookie)
            user = get_user_model().objects.get(id=refresh_token["user_id"])

            data = {
                'access': str(refresh_token.access_token),
                'user': UserSerializer(user, context={"request": request}).data,
            }
            return Response(data)
        except (InvalidToken, TokenError):
            return Response({"detail": "Invalid refresh"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    http_method_names = ['post']
    
    def post(self, request):
        blacklist_refresh_token_from_cookie(request)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        delete_refresh_cookie(response)
        return response


class MeView(APIView):
    http_method_names = ['get', 'put', 'post']
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(pk=request.user.pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        errors = {}

        email = request.data['email']
        if email and User.objects.exclude(pk=request.user.pk).filter(email=email).exists():
            errors = {"email": ["Un utilisateur avec ce courriel existe déjà."]}

        user = User.objects.get(pk=request.user.pk)
        serializer = UserSerializer(user, data=request.data, context={'request': request})
        if not serializer.is_valid():
            errors = merge_errors(errors, serializer.errors)
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data)

    # Suppression avec validation du mot de passe actuel
    def post(self, request):
        serializer = UserDeleteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        blacklist_all_refresh_tokens(user) # On déconnecte tous les périphériques
        user.delete()

        response = Response(status=status.HTTP_204_NO_CONTENT)
        delete_refresh_cookie(response)
        return response


class MePasswordView(APIView):
    http_method_names = ['put']
    permission_classes = [IsAuthenticated]

    # Modification avec validation du mot de passe actuel
    def put(self, request):
        serializer = UserPasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(APIView):
    http_method_names = ['post']

    def post(self, request):
        errors = {}

        email = request.data['email']
        if email and User.objects.filter(email=email).exists():
            errors = {"email": ["Un utilisateur avec ce courriel existe déjà."]}

        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            errors = merge_errors(errors, serializer.errors)
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
