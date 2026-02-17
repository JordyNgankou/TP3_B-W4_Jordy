from django.contrib.auth import password_validation
from django.contrib.auth.models import User, update_last_login
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.serializers import CharField, ModelSerializer, Serializer
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer, ValidationError as DRFValidationError)
from rest_framework_simplejwt.settings import api_settings

from .helpers import blacklist_all_refresh_tokens


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		super().validate(attrs)

		refresh = self.get_token(self.user)
	
		data = {
            'access': str(refresh.access_token),
            'user': UserSerializer(self.user, context=self.context).data,
        }

		self.refresh_token = refresh

		if api_settings.UPDATE_LAST_LOGIN:
			update_last_login(None, self.user)

		return data
  

class RegisterSerializer(ModelSerializer):
	password = CharField(write_only=True)

	class Meta:
		model = User
		fields = ["first_name", "last_name", "email", "username", "password"]

	def validate_password(self, value):
		try:
			password_validation.validate_password(value)
		except DjangoValidationError as e:
			raise DRFValidationError([err.message for err in e.error_list])
		return value

	def create(self, validated_data):
		return User.objects.create_user(**validated_data)


class UserSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = ["first_name", "last_name", "email", "username"]


class UserDeleteSerializer(Serializer):
	current_password = CharField(write_only=True, required=True)

	def validate_current_password(self, value):
		user = self.context['request'].user
		if not user.check_password(value):
			raise DRFValidationError(["Mot de passe actuel incorrect."])
		return value


class UserPasswordSerializer(Serializer):
	current_password = CharField(write_only=True, required=True)
	new_password = CharField(write_only=True, required=True)

	def validate_current_password(self, value):
		user = self.context['request'].user
		if not user.check_password(value):
			raise DRFValidationError(["Mot de passe actuel incorrect."])
		return value
	
	def validate_new_password(self, value):
		try:
			password_validation.validate_password(value, user=self.context['request'].user)
		except DjangoValidationError as e:
			raise DRFValidationError([err.message for err in e.error_list])
		return value

	def save(self):
		user = self.context['request'].user
		user.set_password(self.validated_data['new_password'])
		user.save(update_fields=['password'])

		blacklist_all_refresh_tokens(user) # On déconnecte tous les périphériques

		return user
