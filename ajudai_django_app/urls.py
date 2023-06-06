from django.urls import path
from django.contrib.auth import views as auth_views

from ajudai_django_app import views

urlpatterns = [
    path('', views.welcome_view, name="welcome"),
    path('meu-perfil/', views.user_accounts_view, name="user_accounts"),
    path('meu-plano/', views.meu_plano_view, name="meu-plano"),
    path('dashboard/', views.dashboard_view, name="dashboard"),  
    path('planos-disponiveis/', views.planos_disponiveis_view, name="planos_disponiveis"),    
    path('minhas-conversas/', views.minhas_conversas_view, name='minhas-conversas'),
    path('contato/', views.contato_view, name="contato"),
    path('instrucoes/', views.instrucoes_view, name="instrucoes"),
    path('solicitacao/', views.solicitacao_view, name="solicitacao"),
    path('criacao-chatbot/', views.chatbot_creation_form, name='chatbot_creation_form'),
    path('editar-chatbot/<int:chatbot_id>/', views.editar_chatbot_view, name='chatbot_edit'),
    path('meus-chatbots/', views.meus_chatbots_view, name="meus-chatbots"),
    path('deletar-chatbot/<int:chatbot_id>/', views.chatbot_delete_view, name='chatbot_delete'),
    path('pedidos-realizados/', views.pedidos_realizados_view, name="pedidos-realizados"),
    path('resumo-do-pedido/<int:pedido_id>/', views.resumo_pedido, name='resumo_pedido'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar/', views.register_view, name='register'),
    path('alterar-senha/', views.change_password_view, name='change_password'),
    path('email_sent/', views.send_confirmation_email, name='email_sent'),
    path('email_confirmed/<slug:token>/', views.email_confirmed, name='email_confirmed'),
    path('email_confirm_link_error/', views.email_confirm_link_error, name='email_confirm_link_error'),
    path('delete_account/', views.delete_account_view, name='delete_account'),
    path('esqueci-senha/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('email_redefinicao_enviado/', auth_views.PasswordResetDoneView.as_view(template_name='reset_password_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_password_complete.html'), name='password_reset_complete'),
    path('privacidade/', views.privacy_policy, name='privacidade'),
    path('termos_e_condicoes/', views.terms_and_conditions, name='termos_e_condicoes'),
    path('whatsapp/webhook/', views.whatsapp_message_webhook, name='whatsapp_webhook'),
]