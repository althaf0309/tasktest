"""
task/serializers.py
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from .models import User, Task

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that uses 'email' instead of 'username'.
    Client must send { "email": ..., "password": ... } in POST body.
    """
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('No user found with this email address.')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password.')

        # Create token
        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            # You can add extra user info here if desired
            'role': user.role,
            'email': user.email,
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.ReadOnlyField(source='assigned_to.username')

    class Meta:
        model = Task
        fields = [
            'id', 
            'title', 
            'description', 
            'assigned_to',
            'assigned_to_username',
            'due_date', 
            'status', 
            'completion_report', 
            'worked_hours'
        ]
        read_only_fields = ['completion_report', 'worked_hours']
