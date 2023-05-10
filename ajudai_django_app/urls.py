from django.urls import path
from django.contrib.auth import views as auth_views

from ajudai_django_app import views

urlpatterns = [
    path('', views.user_accounts_view, name="user_accounts"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar/', views.register_view, name='register'),
    path('alterar_senha/', views.change_password_view, name='change_password'),
    path('email_sent/', views.send_confirmation_email, name='email_sent'),
    path('email_confirmed/<slug:token>/', views.email_confirmed, name='email_confirmed'),
    path('email_confirm_link_error/', views.email_confirm_link_error, name='email_confirm_link_error'),
    path('delete_account/', views.delete_account_view, name='delete_account'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='reset_password_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_password_complete.html'), name='password_reset_complete'),
    path('privacidade/', views.privacy_policy, name='privacidade'),
    path('termos_e_condicoes/', views.terms_and_conditions, name='termos_e_condicoes'),
]