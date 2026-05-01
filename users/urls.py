from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (
    UserCreateView, UserProfileView, UserUpdateView, UserListView,
    quick_update_user_role, receptionist_reset_password
)

app_name = 'users'

urlpatterns = [
    path('create-user/', UserCreateView.as_view(), name='create-user'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user-profile'),
    path('list/', UserListView.as_view(), name='users-list'),
    path('profile/<int:pk>/update/', UserUpdateView.as_view(), name='update-user'),
    path('quick-update-role/', quick_update_user_role, name='quick-update-role'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Password Reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html',
                                            email_template_name='users/password_reset_email.html',
                                            subject_template_name='users/password_reset_subject.txt',
                                            success_url=reverse_lazy('users:password_reset_done')), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                                   success_url=reverse_lazy('users:password_reset_complete')), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),

    # Receptionist Reset Password
    path('receptionist-reset-password/<int:user_id>/', receptionist_reset_password, name='receptionist-reset-password'),
]
