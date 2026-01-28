# Path: accounts/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('friends/', views.friends_view, name='friends'),
    path('send-friend-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('respond-friend-request/<int:friendship_id>/<str:action>/', views.respond_friend_request, name='respond_friend_request'),
    path('search/', views.search_users, name='search_users'),
    path('roles/', views.manage_roles, name='manage_roles'),
    path('assign-role/<int:user_id>/<int:role_id>/', views.assign_role, name='assign_role'),
    
]