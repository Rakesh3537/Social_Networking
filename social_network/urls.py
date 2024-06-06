from django.contrib import admin
from django.urls import path, include
from users.views import signup_page, login_page, friends_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('signup/', signup_page, name='signup-page'),
    path('login/', login_page, name='login-page'),
    path('friends/', friends_page, name='friends-page'),
]
