from rest_framework import serializers
from .models import User, Organization
from django.core.validators import validate_email as django_validate_email

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']

class Organizationserializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id'', name', 'description']