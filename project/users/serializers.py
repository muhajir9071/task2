# users/serializers.py

from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from mongoengine.errors import NotUniqueError
import uuid

from .models import User, Token

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        if User.objects(username=data['username']).first():
            raise serializers.ValidationError("Username already exists.")
        if User.objects(email=data['email']).first():
            raise serializers.ValidationError("Email already exists.")
        return data

    def create(self, validated_data):
        # 1. Hash & Save User
        validated_data['password'] = make_password(validated_data['password'])
        try:
            user = User(**validated_data)
            user.save()
        except NotUniqueError:
            raise serializers.ValidationError("Username or email already exists.")

        # 2. Create Token with explicit key
        token = Token(
            user_id=str(user.id),
            key=str(uuid.uuid4())
        )
        token.save()

        return {
            "user": {
                "id":       str(user.id),
                "username": user.username,
                "email":    user.email,
            },
            "token": token.key
        }

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # 1. Verify credentials
        user = User.objects(username=data['username']).first()
        if not user or not check_password(data['password'], user.password):
            raise serializers.ValidationError("Invalid username or password.")

        # 2. Reuse existing token or create new one
        token_obj = Token.objects(user_id=str(user.id)).first()
        if not token_obj:
            token_obj = Token(
                user_id=str(user.id),
                key=str(uuid.uuid4())
            )
            token_obj.save()

        return {
            "user": {
                "id":       str(user.id),
                "username": user.username,
                "email":    user.email,
            },
            "token": token_obj.key
        }

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()

