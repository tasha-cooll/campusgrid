from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Role


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(
        write_only=True, required=True, label="Confirm password")

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email',
                  'phone', 'role', 'password', 'password2']
        extra_kwargs = {
            'email': {'required': True},
            'role':  {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', Role.REQUESTER),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone',
                  'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class ChangeRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['role']
