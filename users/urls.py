from django.urls import path
from .views import SignupView, LoginView, SearchUsersView, FriendRequestView, AcceptRejectFriendRequestView, FriendListView, PendingFriendRequestView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', SearchUsersView.as_view(), name='user-search'),
    path('friend-request/', FriendRequestView.as_view(), name='friend-request'),
    path('friend-request/<int:pk>/', AcceptRejectFriendRequestView.as_view(), name='friend-request-accept-reject'),
    path('friends/', FriendListView.as_view(), name='friend-list'),
    path('friend-requests/', PendingFriendRequestView.as_view(), name='pending-friend-requests'),
]
