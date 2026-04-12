from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from accounts.models import CustomUser

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password")

    @transaction.atomic
    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
