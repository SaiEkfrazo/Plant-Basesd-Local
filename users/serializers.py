from rest_framework import serializers
from .models import User
import re
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number','email']


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_email_or_phone(self, value):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        phone_regex = r'^\+?1?\d{9,15}$'  # Adjust the regex to match your phone number format

        if not (re.match(email_regex, value) or re.match(phone_regex, value)):
            raise serializers.ValidationError("Enter a valid email or phone number")
        
        return value

    def validate(self, data):
        email_or_phone = data.get('email_or_phone')
        if not email_or_phone:
            raise serializers.ValidationError("This field is required")

        return data