from rest_framework import serializers
from .models import User, Organisation

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'phone']

class Organisationserializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['orgId'', name', 'description']