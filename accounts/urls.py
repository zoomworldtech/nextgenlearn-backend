from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomSetPasswordForm


urlpatterns = [
    # ------------------ Authentication ------------------ #
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # ------------------ Admin Dashboard ------------------ #
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ------------------ Admin CRUD ------------------ #
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

    # ------------------ API Routes ------------------ #
    path('api/register/', views.api_register, name='api_register'),
    path('api/login/', views.api_login, name='api_login'),

    # ------------------ Password Reset ------------------ #
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html'
        ),
        name='password_reset'
    ),
    path(
        'password_reset_done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            form_class=CustomSetPasswordForm
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    # ------------------ Homepage ------------------ #
    path('', views.home, name='home'),

    path('approve-courses/', views.approve_courses, name='approve_courses'),
    path('approve-results/', views.approve_results, name='approve_results'),
    path('approve-payments/', views.approve_payments, name='approve_payments'),
]
