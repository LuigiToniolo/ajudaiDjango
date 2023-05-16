from django.shortcuts import render, redirect
from ajudai_django_app.forms import CustomUserCreationForm, LoginForm
from ajudai_django_app.models import CustomUser
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from constants import FANTASY_NAME, PASSWORD_FIELD_ID, SUPPORT_EMAIL, USER_NAME_FIELD_ID
from .forms import CustomPasswordChangeForm
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

def user_accounts_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')

    context = {
        "tab_title" : 'Ajudaí',
        "meta_desciption" : '',
        'user' : user,
        'title_user_page' : 'Seja bem-vindo',
        'user_page_data_title' : 'Veja abaixo os seus dados:',
        'userNameLabel' : 'Nome de Usuário',
        'nomeCompletoLabel' : 'Nome completo',
        'emailLabel' : 'E-mail corporativo',
        'celularLabel' : 'Celular',
        'empresaLabel' : 'Nome da Empresa',
        'segmentoLabel' : 'Segmento',
        'cargoLabel' : 'Cargo atual',
        'delte_account_confirm_message' : 'Você tem certeza que gostaria de deletar a sua conta? Todas as suas informações serão deletadas!',
        'change_password_text' : 'Alterar minha senha',
        'LOGOUT_BUTTON_VALUE' : 'Logout',
        'DELETE_ACCOUNT_BUTTON_VALUE' : 'Deletar Conta',
    }

    return render(
        request,
        "user_accounts.html",  # Path from the 'templates' folder inside the app folder
        context,
    )


def login_view(request):
    login_form = LoginForm()
    context = {
        'title' : 'Login',
        'LINK_TO_REGISTER_TEXT' : 'Registre-se',
        'login_form' : login_form,
        'forgot_password_text': 'Esqueci minha senha',
        'submit_login_text' : 'Acessar',
        'isHome' : False,
    }
    if request.method == 'POST':
        # obtenha os dados do formulário de login aqui
        username = request.POST[USER_NAME_FIELD_ID]
        password = request.POST[PASSWORD_FIELD_ID]
            
        # verifique se os dados de login são válidos usando o método de autenticação do Django
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # autentique o usuário e redirecione para a página inicial
            login(request, user)
            return redirect('/')
        else:
            # exiba o formulário de login novamente com uma mensagem de erro
            error_message = 'Nome de usuário ou senha inválidos'
            context['error_message'] = error_message
            return render(request, 'login.html', context)
    else:
        # exiba o formulário de login
        return render(request, 'login.html', context)
    
def logout_view(request):
    logout(request)
    return redirect('user_accounts')

#--------------Área do usuário-----------------------


def welcome_view(request):
    return render(request, 'welcome.html')


def dashboard_view(request):
    return render(request, 'dashboard.html')



#-------------------------------------------------------

def register_view(request):
    
    if request.method == 'POST':
        # obtenha os dados do formulário de registro aqui
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                CustomUser.register_and_login_new_user(form, request)
                return redirect('email_sent')
            except:
                return redirect('database_error')
        else:
            # exiba o formulário de registro novamente com uma mensagem de erro
            error_message = 'Dados de registro inválidos!'
            context = {
                'title' : 'Registro',
                'form': form,
                'error_message': error_message,
                'registeButtonText' : 'Criar minha conta',
                'isHome' : False,
            }
            return render(request, 'register.html', context)
    else:
        # exiba o formulário de registro
        form = CustomUserCreationForm()
        context = {
            'form': form,
            'registeButtonText' : 'Criar minha conta',
            'isHome' : False,
        }
        return render(request, 'register.html', context)
    
def send_confirmation_email(request):
    try:
        user = CustomUser.getUser(request)
        if not request.user.is_authenticated:
            return redirect('login')
        token = user.email_confirmation_token
    except:
        return redirect('database_error')

    subject = FANTASY_NAME + ' - Confirme seu email'
    message = f'Bem-vindo ao {FANTASY_NAME}! Clique no link a seguir para confirmar o seu email: {request.build_absolute_uri(reverse("email_confirmed", args=[token]))}'
    send_mail(subject, message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email])

    context = {
        'title' : "Confirmação de email enviada",
        'user': user,
        'message': 'Um e-mail de confirmação foi enviado. Verifique sua caixa de entrada (INCLUINDO A CAIXA DE SPAM) e clique no link de confirmação. É comum que os provedores de e-mail direcionem o e-mail para a caixa de spam, então lembre-se de verificar isso também... Lembre-se, para usar nossos serviços, sua conta deve ter um endereço de e-mail confirmado.',
        'message': 'Um e-mail de confirmação foi enviado. Verifique a caixa de entrada e o SPAM. Para usar os serviços do Ajudai é necessário essa confirmação',
        'observation' : 'Se você não receber dentro de alguns minutos, atualize esta página.',
    }
    return render(request, 'email_sent.html', context)

def email_confirmed(request, token):
    User = get_user_model()
    try:
        # retrieve the user associated with the activation token
        user = User.objects.get(email_confirmation_token=token)
        user.email_confirmed = True
        user.email_confirmation_token = ''
        user.save()
        context = {
            'title' : 'Email confirmado',
            'user': user,
            'message': 'Seu email foi confirmado! Obrigado!',
            'observation' : 'Agora você será redirecionado para à página inicial.',
        }
        return render(request, 'email_confirmed.html', context)
    
    except:
        return redirect('email_confirm_link_error')
    
def email_confirm_link_error(request):
    try:
        user = CustomUser.getUser(request)
    except:
        pass

    return render(
        request,
        "email_confirm_link_error.html",
        {
            'title' : "Erro na confirmação de email",
            'error_message' : "Ocorreu um erro ao acessar o link de confirmação do e-mail. Por favor, tente novamente mais tarde. Caso o erro persista entre em contato com nosso suporte:",
            'SUPPORT_EMAIL' : SUPPORT_EMAIL,
            'user' : user,
            'isHome' : False,
        }
    )

def delete_account_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')

    if not request.user.is_authenticated:
        return redirect('login')

    user.delete()
    return redirect('user_accounts')

def change_password_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            return redirect('user_accounts')
        else:
            messages.error(request, 'Por favor, corrija os erros a seguir:')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {
        'title' : "Alteração de Senha",
        'form': form,
        'submit_change_passwird_text' : 'Alterar a senha'
    })

def terms_and_conditions(request):
    try:
        user = CustomUser.getUser(request)
    except:
        pass

    return render(
        request,
        "terms_and_conditions.html",
        {
            'title' : "Termos de Uso",
        }
    )

def privacy_policy(request):
    try:
        user = CustomUser.getUser(request)
    except:
        pass

    return render(
        request,
        "privacy_policy.html",
        {
            'title' : "Política de Privacidade",
        }
    )

def database_error(request):
    try:
        user = CustomUser.getUser(request)
    except:
        pass

    return render(
        request,
        "database_error.html",
        {
            'title' : "Erro no Banco de Dados",
            'error_message' : "Desculpe, parece ter havido um erro ao gravar ou recuperar informações de nossos bancos de dados. Por favor, tente novamente mais tarde. Caso o erro persista entre em contato com nosso suporte:",
            'SUPPORT_EMAIL' : SUPPORT_EMAIL,
            'user' : user,
            'isHome' : False,
        }
    )