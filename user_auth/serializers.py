from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'username': self.user.username,
            'is_staff': self.user.is_staff,
        }

        return data



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'roles']

    def create(self, validated_data):
        password = validated_data.pop('password') 
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LimitedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username',]


class SearchResultSerializer(serializers.Serializer):
    results = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()
    query = serializers.CharField()