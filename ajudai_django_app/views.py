from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, JsonResponse
import pytz
from ajudai_django_app.ai_chatbot.ai_awnser import generate_gpt_response, pedido_confirmado
from ajudai_django_app.ai_chatbot.ai_tools import instructions_over_limit_error_messages, instructions_under_the_limits
from ajudai_django_app.fechamento_de_pedido.procedimento_de_fechamento import informar_loja_fechamento_pedido
from ajudai_django_app.forms import CustomUserCreationForm, LoginForm
from ajudai_django_app.models import Adesao_Purchase, ChatBot, Conversa, CustomUser, Pedido, Premium_User_Payment_Method_Registration, Product, register_adesao_purchase_after_webhook_confirm, register_payment_method_success_after_webhook_confirm, update_conversa_objects
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from ajudai_django_app.payments_process.sign_in import create_stripe_customer, return_adesao_checkout_session, return_checkout_session_id, return_checkout_session_url, return_setup_future_payments_checkout_session
from ajudai_django_app.payments_process.webhooks import HTTP_PAYMENT_API_SIGNATURE, LABEL_TO_CHECKOUT_SESSION_ID, get_session_data, get_usage_payment_webhook_customer, get_webhook_event, success_payment_checkout_and_section_recovery, success_payment_usage_charge
from ajudai_django_app.phone_integration.messages import send_response
from constants import ADESAO_PURCHASE_STATUS_PENDING, ADITIONAL_INTRUCTIONS_FIELD_ID, ADITIONAL_INTRUCTIONS_FIELD_NAME, DOMAIN, EVENT_INVALID_PAYLOAD, EVENT_INVALID_SIGNATURE, FANTASY_NAME, GPT3_MODEL_NAME, GPT3_TOKEK_LIMIT, PASSWORD_FIELD_ID, PAYMENT_METHOD_REGISTRATION_STATUS_PENDING, PRUDUCT_TYPE_ADESAO, STANDART_PERIOD, STATUS_CONVERSA_EM_ANDAMENTO, STATUS_PEDIDO_EM_PROCESSO, STATUS_PEDIDO_ENTREGUE, STATUS_PEDIDO_PENDENTE_DE_ENTREGA, STATUS_PEDIDO_REALIZADO, SUPPORT_EMAIL, USER_LEVEL_PREMIUM, USER_NAME_FIELD_ID, WEBHOOK_ADESAO_ID, WEBHOOK_PAYMENT_METHOD_ID, WEBHOOK_USAGE_PAYMENT_ID
from get_secret_variables import get_secret_var
from .forms import ChatBotForm, CustomPasswordChangeForm, MessageForm
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
from django_q.tasks import async_task
import stripe
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField

sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

def welcome_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {
        "tab_title" : 'Bem Vindo ao Ajudaí',
        'user' : user,
        'userIsPremium' : user.userIsPremium(),
    }

    user.finance_check(STANDART_PERIOD)

    return render(request, 'welcome.html', context)

def user_accounts_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    user.finance_check(STANDART_PERIOD)

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
        'userIsPremium' : user.userIsPremium(),
    }

    return render(
        request,
        "user_accounts.html",  # Path from the 'templates' folder inside the app folder
        context,
    )

def dashboard_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not user.userIsPremium():
        return redirect('planos_disponiveis')
    
    if not user.usuario_adimplente_ou_tolerancia_de_uso():
        return redirect('payment_debt_out_service')
    
    user.finance_check(STANDART_PERIOD)
    
    #TODO
    context = {
        'userIsPremium' : user.userIsPremium(),
    }

    return render(request, 'dashboard.html', context)

def meus_chatbots_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not user.userIsPremium():
        return redirect('planos_disponiveis')
    
    if not user.usuario_adimplente_ou_tolerancia_de_uso():
        return redirect('payment_debt_out_service')
    
    user.finance_check(STANDART_PERIOD)
    
    chatbots = ChatBot.objects.filter(user=user)

    context = {
        'user' : user,
        'chatbots' : chatbots,
        'userIsPremium' : user.userIsPremium(),
    }
    return render(request, 'meus-chatbots.html', context)

def planos_disponiveis_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')

    context = {
        'user' : user,
        'userIsPremium' : user.userIsPremium(),
    }

    return render(request, 'planos_disponiveis.html', context)

def meu_plano_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not user.userIsPremium():
        return redirect('planos_disponiveis')
    
    if not user.usuario_adimplente_ou_tolerancia_de_uso():
        return redirect('payment_debt_out_service')
    
    user.finance_check(STANDART_PERIOD)

    context = {
        'user' : user,
        'userIsPremium' : user.userIsPremium(),
    }
    #TODO APÓS INTEGRAÇÃO COM PAGAMENTOD
    return render(request, 'meu-plano.html', context)

def minhas_conversas_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not user.userIsPremium():
        return redirect('planos_disponiveis')
    
    if not user.usuario_adimplente_ou_tolerancia_de_uso():
        return redirect('payment_debt_out_service')
    
    user.finance_check(STANDART_PERIOD)

    Conversa.close_conversa_if_needed(user)

    chatbots = ChatBot.objects.filter(user=user)
    conversas = Conversa.objects.filter(chatbot__in=chatbots).annotate(
        status_order=Case(
            When(status_da_conversa=STATUS_CONVERSA_EM_ANDAMENTO, then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by('status_order', 'date', 'time')

    conversas_com_tempo_das_mensagens = []
    for conversa in conversas:
        if len(conversa.context) == len(conversa.messages_display_time):
            merged_context = []
            for i in range(len(conversa.context)):
                # Merge dictionaries at the same index
                merged_item = {**conversa.context[i], **conversa.messages_display_time[i]}
                merged_context.append(merged_item)
            # Replace the original context with the merged context
            conversa.context = merged_context
            # Append the updated conversa object to the new list
            conversas_com_tempo_das_mensagens.append(conversa)
        else:
            # handle the case when the lengths don't match, e.g., log an error or raise an exception
            pass


    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.cleaned_data['message']
            conversa_id= form.cleaned_data['conversa_id']
            conversa= get_object_or_404(Conversa, id=conversa_id)
            chatbot= conversa.chatbot
            conversa.add_message_to_conversa(new_message, "assistant")
            send_response(chatbot.facebook_page_id, chatbot.whats_app_api_auth_token, conversa.company_client_number, new_message)
            conversa.update_conversa_time_date()
            updated_conversa_id = conversa_id
        else:
            updated_conversa_id = None
    else:
        updated_conversa_id = None

    context = {
        "tab_title" : 'Ajudaí - Minhas Conversas',
        "meta_desciption" : '',
        'user' : user,
        'conversas' : conversas_com_tempo_das_mensagens,
        'updated_conversa_id': updated_conversa_id,
        'userIsPremium' : user.userIsPremium(),
    }
    return render(
        request,
        "minhas-conversas.html",  # Path from the 'templates' folder inside the app folder
        context,
    )

@csrf_exempt
def check_for_new_messages_to_refresh(request):
    if request.method == 'POST':
        try:
            user = CustomUser.getUser(request)
        except: 
            return JsonResponse({"error": "Unauthorized access"}, status=401)
        
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Unauthorized access"}, status=401)

        chatbots = ChatBot.objects.filter(user=user)
        conversas = Conversa.objects.filter(chatbot__in=chatbots)

        should_refresh = any(conversa.need_refresh_view for conversa in conversas)

        if should_refresh:
            for conversa in conversas:
                conversa.need_refresh_view = False
                conversa.save()

        # Return a JsonResponse indicating whether to refresh or not
        return JsonResponse({"should_refresh": should_refresh})

    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
@csrf_exempt
def update_last_message_shown(request, conversa_id):
    if request.method == 'POST':
        conversa = get_object_or_404(Conversa, id=conversa_id)
        if request.user != conversa.chatbot.user:
            return JsonResponse({"error": "Unauthorized access"}, status=401)
        conversa.last_message_shown = True
        conversa.save()
        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

def toggle_chatbot(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        conversa_id = request.POST.get('conversa_id')
        conversa = Conversa.objects.get(id=conversa_id)

        if conversa.chatbot.user != user:
            return JsonResponse({'status': 'error'})

        conversa.chatbot_ativo = not conversa.chatbot_ativo
        conversa.save()

        mensagem_de_aviso = ''
        chatbot = conversa.chatbot

        if conversa.chatbot_ativo:
            mensagem_de_aviso = 'A partir de agora, o chatbot que dá respostas utilizando inteligência artificial foi retomado!'
        else:
            mensagem_de_aviso = 'A partir de agora você estará conversando com uma pessoa! O chatbot foi desativado!'

        send_response(chatbot.facebook_page_id, chatbot.whats_app_api_auth_token, conversa.company_client_number, mensagem_de_aviso)  
        conversa.update_conversa_time_date() 
        conversa.add_message_to_conversa(mensagem_de_aviso, "assistant")
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})

def editar_chatbot_view(request, chatbot_id):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not user.userIsPremium():
        return redirect('planos_disponiveis')
    
    if not user.usuario_adimplente_ou_tolerancia_de_uso():
        return redirect('payment_debt_out_service')

    user.finance_check(STANDART_PERIOD)

    chatbot = get_object_or_404(ChatBot, id=chatbot_id)

    if request.user != chatbot.user:
        return redirect('login')

    if request.method == 'POST':
        form = ChatBotForm(request.POST, instance=chatbot)

        if form.is_valid():
            form.save()
            return redirect('meus-chatbots')
    else:
        form = ChatBotForm(instance=chatbot)

    context = {
        "tab_title" : 'Edição de Chatbot',
        'chatbot': chatbot,
        'form': form,
        "meta_desciption" : '',
        'user' : user,
        'page_title' : 'Edite seu Chatbot',
        'submit_edit_chatbot_text' : 'Salvar as alterações',
        'delete_edit_chatbot_text' : 'Deletar o Chatbot',
        'userIsPremium' : user.userIsPremium(),
    }

    return render(
        request,
        "editar-chatbot.html", 
        context,
    )

def chatbot_delete_view(request, chatbot_id):
    
    chatbot = get_object_or_404(ChatBot, id=chatbot_id)

    if request.user != chatbot.user:
        return redirect('login')

    if request.method == 'POST':
        chatbot.delete()
        return redirect('user_accounts')
    
    return redirect('user_accounts')

def pedidos_realizados_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not user.userIsPremium():
        return redirect('planos_disponiveis')
    
    user.finance_check(STANDART_PERIOD)

    pedidos = Pedido.objects.filter(user=user)

    if not user.usuario_adimplente_ou_tolerancia_de_uso():
        return redirect('payment_debt_out_service')

    context = {
        "tab_title" : 'Pedidos',
        "meta_desciption" : '',
        'page_title' : 'Pedidos',
        'texto_link_para_resumo_pedido' : 'Veja o Resumo do Pedido',
        'user' : user,
        'pedidos' : pedidos,
        'STATUS_PEDIDO_REALIZADO' : STATUS_PEDIDO_REALIZADO,
        'STATUS_PEDIDO_EM_PROCESSO' : STATUS_PEDIDO_EM_PROCESSO,
        'STATUS_PEDIDO_PENDENTE_DE_ENTREGA' : STATUS_PEDIDO_PENDENTE_DE_ENTREGA,
        'STATUS_PEDIDO_ENTREGUE' : STATUS_PEDIDO_ENTREGUE,
        'userIsPremium' : user.userIsPremium(),
    }

    return render(
        request,
        "pedidos-realizados.html",  # You need to create this template
        context,
    )

def resumo_pedido(request, pedido_id):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not user.userIsPremium():
        return redirect('planos_disponiveis')
    
    if not user.usuario_adimplente_ou_tolerancia_de_uso():
        return redirect('payment_debt_out_service')
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    conversa = pedido.conversa

    if pedido.criado_manualmente == False:
        numero_cliente_pedido = conversa.company_client_number
    else:
        numero_cliente_pedido = '0'

    context = {
        "tab_title" : 'Resumo do Pedido',
        'pedido': pedido,
        "meta_desciption" : '',
        'user' : user,
        'page_title' : 'Resumo do Pedido',
        'label_status_pedido' : 'Status do Pedido',
        'label_resumo_pedido' : 'Resumo do Pedido',
        'label_numero_cliente_pedido' : 'Número Whatsapp do Cliente',
        'numero_cliente_pedido' : numero_cliente_pedido,
        'userIsPremium' : user.userIsPremium(),
    }

    return render(
        request,
        "resumo_pedido.html",  # You need to create this template
        context,
    )

@csrf_exempt
def update_pedido_status(request):
    if request.method == 'POST':
        try:
            user = CustomUser.getUser(request)
        except: 
            return JsonResponse({"error": "Unauthorized access"}, status=401)
        
        pedido_id = request.POST.get('pedido_id')
        new_status = request.POST.get('new_status')

        # Update the status of the Pedido object
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            if request.user != pedido.user:
                return JsonResponse({"error": "Unauthorized access"}, status=401)
            pedido.status_do_pedido = new_status
            pedido.save()
            if pedido.criado_manualmente == False:
                conversa = pedido.conversa
                chatbot = conversa.chatbot
                send_response(chatbot.facebook_page_id, chatbot.whats_app_api_auth_token, conversa.company_client_number, pedido.mensagem_novo_status())
                conversa.update_conversa_time_date()
            return JsonResponse({'status': 'success'})
        except Pedido.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Pedido not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@csrf_exempt
def create_pedido_manual(request):
    if request.method == 'POST':
        try:
            user = CustomUser.getUser(request)
        except: 
            return JsonResponse({"error": "Unauthorized access"}, status=401)
        
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Unauthorized access"}, status=401)
        
        nome_pedido_manual = request.POST.get('nome_pedido_manual')
        pedido = Pedido(
            user=user, criado_manualmente=True, 
            nome_pedido_manual=nome_pedido_manual, 
            status_do_pedido=STATUS_PEDIDO_REALIZADO
            )
        pedido.save()

        return JsonResponse({'status': 'success', 'pedido_id': pedido.id})
    else:
        return JsonResponse({'status': 'failed'})
def login_view(request):
    login_form = LoginForm()
    context = {
        'title' : 'Login',
        'LINK_TO_REGISTER_TEXT' : 'Registre-se',
        'login_form' : login_form,
        'forgot_password_text': 'Esqueci minha senha',
        'submit_login_text' : 'Acessar',
        'isHome' : False,
        'userIsPremium' : False,
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
                'userIsPremium' : False,
            }
            return render(request, 'register.html', context)
    else:
        # exiba o formulário de registro
        form = CustomUserCreationForm()
        context = {
            'form': form,
            'registeButtonText' : 'Criar minha conta',
            'isHome' : False,
            'userIsPremium' : False,
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
        'userIsPremium' : False,
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
            'userIsPremium' : False,
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
            'userIsPremium' : False,
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
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
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
        'submit_change_passwird_text' : 'Alterar a senha',
        'userIsPremium' : user.userIsPremium(),
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
            'userIsPremium' : user.userIsPremium(),
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
            'userIsPremium' : user.userIsPremium(),
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
            'userIsPremium' : user.userIsPremium(),
        }
    )

def chatbot_creation_form(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not user.userIsPremium():
        return redirect('planos_disponiveis')
    
    if not user.usuario_adimplente_ou_tolerancia_de_uso():
        return redirect('payment_debt_out_service')
    
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
        'userIsPremium' : user.userIsPremium(),
    }

    return render(
        request,
        "chatbot_creation_form.html",  # Path from the 'templates' folder inside the app folder
        context,
    )

def contato_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    context = {
        "tab_title" : 'Contato',
        'user' : user,
        "meta_desciption" : '',
        'userIsPremium' : user.userIsPremium(),
    }
    return render(request, 'contato.html', context)

def instrucoes_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    context = {
        "tab_title" : 'Instruções',
        'user' : user,
        "meta_desciption" : '',
        'userIsPremium' : user.userIsPremium(),
    }

    return render(request, 'instrucoes.html', context)

def solicitacao_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    context = {
        "tab_title" : 'Solicitação',
        'user' : user,
        "meta_desciption" : '',
        'userIsPremium' : user.userIsPremium(),
    }

    return render(request, 'solicitacao.html', context)


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
        async_task(process_message, data)
        return HttpResponse('Message received and will be processed', status=200)
        
        
    return HttpResponse('Received invalid request', status=200)

def process_message(data):
    if 'object' in data and 'entry' in data:
            if data['object'] == 'whatsapp_business_account':
                try:
                    for entry in data['entry']:
                        if 'changes' in entry and 'messages' in entry['changes'][0]['value']:
                            numero_cliente = entry['changes'][0]['value']['messages'][0]['from']
                            incoming_message = entry['changes'][0]['value']['messages'][0]['text']['body']
                            company_number_with_DDI =  entry['changes'][0]['value']['metadata']['display_phone_number']
                            #AQUI, COMO NO BANCO DE DADOS, O WHATSAPP EMPRESARIAL DO CLIENTE É REGISTRADO SEM O DDI (55 PARA BRASIL), ELE É PARA LOCALIZAÇÃO DO CLIENTE NO BANCO DE DADOS
                            company_number = company_number_with_DDI[2:]
                            chatbot= get_object_or_404(ChatBot, whatsapp_number=company_number)
                            aditional_instructions = chatbot.aditional_intructions

                            user=chatbot.user

                            #antes de verificar se tem uma conversa aberta em andamento, faz o fechamento daquelas que estão inativas ou esgotaram o tempo
                            Conversa.close_conversa_if_needed(user)

                            if not user.usuario_adimplente_ou_tolerancia_de_uso:
                                return
                            
                            # Get or create a conversation for the phone number
                            try:
                                conversation = Conversa.objects.get(
                                    company_client_number=numero_cliente,
                                    chatbot=chatbot,
                                    status_da_conversa=STATUS_CONVERSA_EM_ANDAMENTO
                                )
                            except:
                                if user.can_create_new_messages(STANDART_PERIOD):
                                    conversation = Conversa.objects.create(
                                        company_client_number=numero_cliente,
                                        chatbot=chatbot,
                                        creation_date=timezone.now().astimezone(sao_paulo_tz).date(),
                                        creation_time=timezone.now().astimezone(sao_paulo_tz).time(),
                                    )
                                else:
                                    return
                            new_context = []
                            if conversation.chatbot_ativo == True:
                                role = ''
                                try:
                                    gpt_response, new_context, tokens_used_on_this_request = generate_gpt_response(incoming_message, conversation.context, role,  aditional_instructions, GPT3_MODEL_NAME, GPT3_TOKEK_LIMIT)
                                except Exception as e:
                                    print ('Erro ao chamar função de resposta IA: ', e)
                                    return

                                conversa_finalizada_com_pedido, resumo = pedido_confirmado(gpt_response)
                                if conversa_finalizada_com_pedido:
                                    user=chatbot.user
                                    pedido = Pedido.objects.create(
                                        user=user,
                                        conversa=conversation,
                                        resumo_do_pedido = resumo,
                                    )
                                    informar_loja_fechamento_pedido(resumo, company_number)
                                    
                                #chama função que responde o cliente da loja via integência artificial
                                send_response(chatbot.facebook_page_id, chatbot.whats_app_api_auth_token, numero_cliente, gpt_response)

                                conversation.substitute_conversa_context(new_context)
                                tokens_used_before = conversation.total_tokens_used
                                conversation.total_tokens_used = tokens_used_before + tokens_used_on_this_request
                                conversation.last_message_shown = False
                                conversation.need_refresh_view = True
                                conversation.date = timezone.now().astimezone(sao_paulo_tz).date()
                                conversation.time = timezone.now().astimezone(sao_paulo_tz).time()
                                conversation.save()
                            
                                return
                            
                            #case no response was created by ai, just saves the message in the context
                            new_context = conversation.context
                            new_context.append({"role": "user", "content": incoming_message})
                            tokens_used_on_this_request = 0
                            conversation.substitute_conversa_context(new_context)
                            tokens_used_before = conversation.total_tokens_used
                            conversation.total_tokens_used = tokens_used_before + tokens_used_on_this_request
                            conversation.last_message_shown = False
                            conversation.need_refresh_view = True
                            conversation.date = timezone.now().astimezone(sao_paulo_tz).date()
                            conversation.time = timezone.now().astimezone(sao_paulo_tz).time()
                            conversation.save()
                            return

                        else:
                            return
                except:
                    return
            else: 
                return

    return

def payment_method_checkout(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')

    if not request.user.is_authenticated:
        return redirect('login')
    
    stripe.api_key = get_secret_var("STRIPE_SECRET_KEY")
    
    try:
        create_stripe_customer(user)
        checkout_session = return_setup_future_payments_checkout_session(DOMAIN + '/metodo-pagamento-registrado', DOMAIN + '/metodo-pagamento-falhou', user)
    except Exception as e:
        return redirect('pricing')
    
    user_payment_method_setup_attempt_registered = False 

    try:
        register_payment_setup_attempt, created = Premium_User_Payment_Method_Registration.objects.update_or_create(
            user=user, 
            defaults={
                'date': timezone.datetime.now().date(),
                'time': timezone.datetime.now().time(),
                'stripe_checkout_id': return_checkout_session_id(checkout_session),
                'status': PAYMENT_METHOD_REGISTRATION_STATUS_PENDING,
            }
        )
        user_payment_method_setup_attempt_registered = True
    except:
        return redirect('database_error')
    
    if user_payment_method_setup_attempt_registered:
        return redirect(return_checkout_session_url(checkout_session), code=303)
    else:
        return redirect('database_error')

def payment_method_success(request):
    try:
        user = CustomUser.getUser(request)
    except:
        pass
    
    context = {
        "tab_title" : 'Processado com Sucesso',
        'user' : user,
        "meta_desciption" : '',
        'userIsPremium' : user.userIsPremium(),
    }

    return render(
        request,
        "sucesso-pagamento.html",
        context
    )

def payment_method_failure(request):
    try:
        user = CustomUser.getUser(request)
    except:
        pass

    context = {
        "tab_title" : 'Falha no Processamento',
        'user' : user,
        "meta_desciption" : '',
        'userIsPremium' : user.userIsPremium(),
    }

    return render(
        request,
        "falha-pagamento.html",
        context
    )

def adesao_payment_checkout(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')

    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        product = Product.objects.get(tipo_de_produto=PRUDUCT_TYPE_ADESAO)
    except:
        return redirect('database_error')
    
    try:
        checkout_session = return_adesao_checkout_session(product.priceID, DOMAIN + '/adesao-realizada', DOMAIN + '/adesao-falhou')
    except:
        return redirect('planos_disponiveis')
    
    purchase_database_register_success = False
    try:
        purchase = Adesao_Purchase.objects.create(
            date= timezone.datetime.now().date(),
            time= timezone.datetime.now().time(),
            product=product,
            user=user,
            stripe_checkout_id=return_checkout_session_id(checkout_session),
            status=ADESAO_PURCHASE_STATUS_PENDING,
            )
        purchase_database_register_success = True
    except:
        return redirect('database_error')
    
    #redundância proposital para garantir que o sessão se checkout venha apenas após o registro da tentativa de compra no banco de dados
    if purchase_database_register_success:
        #dessa forma, leva o usuário à própria página de procesamentento de pagameto / checkout da stripe
        return redirect(return_checkout_session_url(checkout_session), code=303)
    else:
        return redirect('database_error')
    
def adesao_payment_success(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')

    if not request.user.is_authenticated:
        return redirect('login')
    
    return redirect('checkout_metodo_pagamento')

def adesao_payment_failiure(request):
    try:
        user = CustomUser.getUser(request)
    except:
        pass

    return render(
        request,
        "falha-pagamento.html",
        {
            'title' : "Processado com Sucesso",
            'user' : user,
            'userIsPremium' : user.userIsPremium(),
        }
    )

@csrf_exempt
def adesao_payment_webhook(request):
    payload = request.body
    sig_header = request.META[HTTP_PAYMENT_API_SIGNATURE]
    event = None
    
    event = get_webhook_event(payload, sig_header, WEBHOOK_ADESAO_ID)

    if event == EVENT_INVALID_PAYLOAD:
        return HttpResponse(status=400)

    if event == EVENT_INVALID_SIGNATURE:
        return HttpResponse(status=400)

    if success_payment_checkout_and_section_recovery(event):
        
        session = get_session_data(event)
        checkout_id = session[LABEL_TO_CHECKOUT_SESSION_ID]
        
        register_adesao_purchase_after_webhook_confirm(checkout_id)

    # Passed signature verification
    return HttpResponse(status=200)

@csrf_exempt
def payment_method_webhook(request):
    payload = request.body
    sig_header = request.META[HTTP_PAYMENT_API_SIGNATURE]
    event = None
    
    event = get_webhook_event(payload, sig_header, WEBHOOK_PAYMENT_METHOD_ID)

    if event == EVENT_INVALID_PAYLOAD:
        return HttpResponse(status=400)

    if event == EVENT_INVALID_SIGNATURE:
        return HttpResponse(status=400)

    if success_payment_checkout_and_section_recovery(event):
        
        session = get_session_data(event)
        checkout_id = session[LABEL_TO_CHECKOUT_SESSION_ID]
        
        register_payment_method_success_after_webhook_confirm(checkout_id)

    # Passed signature verification
    return HttpResponse(status=200)

@csrf_exempt
def usage_payment_webhook(request):
    payload = request.body
    sig_header = request.META[HTTP_PAYMENT_API_SIGNATURE]
    event = None

    event = get_webhook_event(payload, sig_header, WEBHOOK_USAGE_PAYMENT_ID)

    if event == EVENT_INVALID_PAYLOAD:
        return HttpResponse(status=400)

    if event == EVENT_INVALID_SIGNATURE:
        return HttpResponse(status=400)

    if success_payment_usage_charge(event):
        try:
            customer_id, amount_payed = get_usage_payment_webhook_customer(event)
            user = CustomUser.objects.get(stripe_id=customer_id)
            Conversa.register_payed_conversations(user, amount_payed)
            user.reduce_debt_amount(amount_payed)
            return HttpResponse(status=200)
        except Exception as e:
            print(f'Erro processando o sucesso de pagamento de uso: {str(e)}')
            return HttpResponseServerError('Error processing request')

    # Passed signature verification
    return HttpResponseServerError('Error processing request')

#destino do direcionamento de usuários em dívida acima do tempo de tolerância
def user_in_debt_and_out_of_service_view(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')

    valor_em_divida = user.valor_em_debito

    return render(
        request,
        "user_in_debt.html",
        {
            'title' : "Fora de Serviço",
            'user' : user,
            'valor_em_divida' : valor_em_divida,
            'userIsPremium' : user.userIsPremium(),
        }
    )

def pay_debit(request):
    try:
        user = CustomUser.getUser(request)
    except:
        return redirect('database_error')
    
    if not request.user.is_authenticated:
        return redirect('login')
        
    user.charge_all_user_debt()

    return render(
        request,
        "processando-pagamento-debito.html",
        {
            'title' : "Tentativa de pagamento",
            'user' : user,
            'userIsPremium' : user.userIsPremium(),
        }
    )

