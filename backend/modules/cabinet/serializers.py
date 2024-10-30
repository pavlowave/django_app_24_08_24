from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'first_name', 'last_name', 'photo', 'qr_code','phone', 'entry_time', 'in_gym', 'club', 'gender', 'birth_date']
