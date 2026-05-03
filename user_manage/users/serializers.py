from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import AccessRoleRule, MyUser


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = MyUser
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password2",
        )

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Пароли не совпадают.")
        return data

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        user = MyUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = authenticate(username=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Неверные учетные данные.")
        if not user.is_active:
            raise serializers.ValidationError("Учетная запись не активна.")
        data["user"] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о пользователе."""

    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = MyUser
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role_name",
            "is_active",
        )


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    element_name = serializers.CharField(source="element.name", read_only=True)

    class Meta:
        model = AccessRoleRule
        fields = "__all__"
