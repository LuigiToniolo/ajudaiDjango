from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from ajudai_django_app.ai_chatbot.ai_awnser import generate_gpt_response, pedido_confirmado
from ajudai_django_app.ai_chatbot.ai_tools import instructions_over_limit_error_messages, instructions_under_the_limits
from ajudai_django_app.fechamento_de_pedido.procedimento_de_fechamento import informar_loja_fechamento_pedido
from ajudai_django_app.forms import CustomUserCreationForm, LoginForm
from ajudai_django_app.models import ChatBot, Conversa, CustomUser
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from ajudai_django_app.phone_integration.messages import send_response
from constants import ADITIONAL_INTRUCTIONS_FIELD_ID, ADITIONAL_INTRUCTIONS_FIELD_NAME, FANTASY_NAME, GPT3_MODEL_NAME, GPT3_TOKEK_LIMIT, PASSWORD_FIELD_ID, STATUS_CONVERSA_PEDIDO_REALIZADO, SUPPORT_EMAIL, USER_NAME_FIELD_ID
from get_secret_variables import get_secret_var
from .forms import ChatBotForm, CustomPasswordChangeForm
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404

def user_accounts_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    chatbots = ChatBot.objects.filter(user=user)

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
        'create_chatbot_button_text' : 'Criar meu Chatbot para Whatsapp',
        'delte_account_confirm_message' : 'Você tem certeza que gostaria de deletar a sua conta? Todas as suas informações serão deletadas!',
        'change_password_text' : 'Alterar minha senha',
        'LOGOUT_BUTTON_VALUE' : 'Logout',
        'DELETE_ACCOUNT_BUTTON_VALUE' : 'Deletar Conta',
        'chatbots_list_title' : 'Meus chatbots ativos',
        'no_chatbots_text' : 'Você ainda não possui nenhum chatbot ativo. Para começar, clique no botão de criação abaixo!',
        'chatbots' : chatbots,
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
        'LINK_TO_REGISTER_TEXT' : 'Ainda não possui uma conta? Registre aqui',
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
            return redirect('user_accounts')
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

def chatbot_creation_form(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = ChatBotForm(request.POST)
        if form.is_valid():
            instructions = form.cleaned_data[ADITIONAL_INTRUCTIONS_FIELD_NAME]
            if not instructions_under_the_limits(instructions, GPT3_MODEL_NAME, GPT3_TOKEK_LIMIT):
                form.add_error(ADITIONAL_INTRUCTIONS_FIELD_NAME, instructions_over_limit_error_messages(GPT3_MODEL_NAME, instructions, GPT3_TOKEK_LIMIT))
            else:
                try:
                    chatbot = form.save(commit=False)
                    chatbot.user = request.user
                    chatbot.save()
                    return redirect('user_accounts')
                except Exception as e:
                    form.add_error(None, f"Ocorreu um erro ao tentar criar o chatbot: {str(e)}")

    else:
        form = ChatBotForm()

    context = {
        "tab_title" : 'Crie seu Chatbot',
        'user' : user,
        "meta_desciption" : '',
        'page_title' : 'Crie seu Chatbot',
        'form' : form,
        'submit_button_text' : 'Ativar ChatBot',
        'chatbot_create_password_label' : 'Create Chatbot Password:',
        'ADITIONAL_INTRUCTIONS_FIELD_ID' : ADITIONAL_INTRUCTIONS_FIELD_ID,
    }

    return render(
        request,
        "chatbot_creation_form.html",  # Path from the 'templates' folder inside the app folder
        context,
    )



WEBHOOK_TOKEN = get_secret_var('WHATAPP_WEBHOOK_TOKEN')

@csrf_exempt
def whatsapp_message_webhook(request):
    if request.method == 'GET':    
        VERIFY_TOKEN = WEBHOOK_TOKEN
        mode = request.GET['hub.mode']
        token = request.GET['hub.verify_token']
        challenge = request.GET['hub.challenge']

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse('error', status=403)
        # Get the incoming message
    
    if request.method == 'POST':   

        data = json.loads(request.body)
        if 'object' in data and 'entry' in data:
            if data['object'] == 'whatsapp_business_account':
                try:
                    for entry in data['entry']:
                        company_client_number = entry['changes'][0]['value']['messages'][0]['from']
                        incoming_message = entry['changes'][0]['value']['messages'][0]['text']['body']
                        company_number_with_DDI =  entry['changes'][0]['value']['metadata']['display_phone_number']
                        #AQUI, COMO NO BANCO DE DADOS, O WHATSAPP EMPRESARIAL DO CLIENTE É REGISTRADO SEM O DDI (55 PARA BRASIL), ELE É PARA LOCALIZAÇÃO DO CLIENTE NO BANCO DE DADOS
                        company_number = company_number_with_DDI[2:]
                        chatbot= get_object_or_404(ChatBot, whatsapp_number=company_number)
                        aditional_instructions = chatbot.aditional_intructions
                        # Get or create a conversation for the phone number
                        conversation, _ = Conversa.objects.get_or_create(
                            company_client_number =company_client_number,
                            chatbot=chatbot,
                            )
                        role = 'Você é um atendente virtual que auxilia o cliente a fazer o pedido através das informações a seguir.'
        
                        gpt_response, new_context, tokens_used_on_this_request = generate_gpt_response(incoming_message, conversation, role,  aditional_instructions, GPT3_MODEL_NAME, GPT3_TOKEK_LIMIT)

                        conversa_finalizada, resumo = pedido_confirmado(gpt_response)
                        if conversa_finalizada:
                            conversation.status_da_conversa = STATUS_CONVERSA_PEDIDO_REALIZADO
                            conversation.resumo_do_pedido_gerado_com_a_conversa = resumo
                            informar_loja_fechamento_pedido(resumo, company_number)

                        conversation.context = new_context
                        tokens_used_before = conversation.total_tokens_used
                        conversation.total_tokens_used = tokens_used_before + tokens_used_on_this_request
                        conversation.save()

                        #chama função que responde o cliente da loja via integência artificial
                        send_response(chatbot.facebook_page_id, chatbot.whats_app_api_auth_token, company_client_number, gpt_response)
                    
                    return HttpResponse('Message received and awnsered', status=200)
                
                except:
                    pass
        
    
    return HttpResponse('Invalid request', status=400)