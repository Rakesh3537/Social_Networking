from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from .serializers import UserSerializer, FriendRequestSerializer
from .models import FriendRequest
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class SignupView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email__iexact=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            username = user.email
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': username, 
            })
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



class SearchUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return User.objects.filter(
            models.Q(email__icontains=query) | 
            models.Q(first_name__icontains=query) | 
            models.Q(last_name__icontains=query)
        )

class FriendRequestView(generics.ListCreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)

    def perform_create(self, serializer):
        to_user = serializer.validated_data.get('to_user')
        from_user = self.request.user

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status='pending').exists():
            raise serializers.ValidationError("You have already sent a friend request to this user.")
        
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(from_user=from_user, created_at__gte=one_minute_ago).count()
        if recent_requests >= 3:
            raise serializers.ValidationError("You can only send 3 friend requests per minute.")
        
        serializer.save(from_user=from_user)

class AcceptRejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        friend_request = FriendRequest.objects.filter(pk=pk, to_user=request.user, status='pending').first()
        if not friend_request:
            return Response({"detail": "Friend request not found or already responded to."}, status=status.HTTP_404_NOT_FOUND)
        
        action = request.data.get('action')
        if action == 'accept':
            friend_request.status = 'accepted'
        elif action == 'reject':
            friend_request.status = 'rejected'
        else:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request.save()
        return Response({"status": friend_request.status}, status=status.HTTP_200_OK)

class FriendListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return User.objects.filter(
            models.Q(sent_requests__to_user=self.request.user, sent_requests__status='accepted') |
            models.Q(received_requests__from_user=self.request.user, received_requests__status='accepted')
        ).distinct()

class PendingFriendRequestView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status='pending')


def signup_page(request):
    return render(request, 'users/signup.html')

def login_page(request):
    return render(request, 'users/login.html')

def friends_page(request):
    return render(request, 'users/friends.html')
