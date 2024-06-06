#users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FriendRequest
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']
        read_only_fields = ['id', 'from_user', 'status', 'created_at']

    def get_from_user(self, obj):
        return UserSerializer(obj.from_user).data

    def create(self, validated_data):
        to_user = validated_data.get('to_user')
        from_user = self.context['request'].user

        # Check if the request already exists
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status='pending').exists():
            raise serializers.ValidationError("You have already sent a friend request to this user.")
        
        # Check rate limit
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(from_user=from_user, created_at__gte=one_minute_ago).count()
        if recent_requests >= 3:
            raise serializers.ValidationError("You can only send 3 friend requests per minute.")

        friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return friend_request
