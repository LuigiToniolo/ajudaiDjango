import time
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import Group, Permission
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Q
from ajudai_django_app.ai_chatbot.ai_extration import ai_gpt_extrair_dado_do_resumo, ai_gpt_extrair_endereco_do_resumo
from ajudai_django_app.payments_process.charge_usage import charge_usages
from ajudai_django_app.phone_integration.messages import send_response
import pytz
import re
from decimal import Decimal
import re
from unidecode import unidecode
from django.core.exceptions import ObjectDoesNotExist
from constants import ADESAO_PURCHASE_STATUS_CALCELED, ADESAO_PURCHASE_STATUS_PENDING, ADESAO_PURCHASE_STATUS_PROCESSED, AI_PROVIDER_OPEN_AI, API_MAX_ATTEMP, BRL_CURRENCY_SIMBOL, CONVERSA_AGUARDANDO_VENCIMENTO, CONVERSA_PAGA, CONVERSA_PAGAMENTO_PENDENTE, DIAS_TOLERACIA_INADIMPLECIA, FATURA_PAGA, FATURA_PENDENTE, GPT3_MODEL_NAME, HOURS_TO_RESER_ABSOLUTE, HOURS_TO_RESET_INACTIVE, LIMITE_CONVERSAS_PLANO_PLUS, LIMITE_CONVERSAS_PLANO_PREMIUM, LIMITE_CONVERSAS_PLANO_STANDARD, MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, MENSAGEM_ENCERRAMENTO_DE_CONVERSA_INATIVIDADE, MENSAGEM_ENCERRAMENTO_DE_CONVERSA_TEMPO_LIMITE, PAYMENT_METHOD_BOLETO, PAYMENT_METHOD_CREDIT_CARD, PAYMENT_METHOD_OTHER, PAYMENT_METHOD_PIX, PAYMENT_METHOD_REGISTRATION_STATUS_FAILING, PAYMENT_METHOD_REGISTRATION_STATUS_PENDING, PAYMENT_METHOD_REGISTRATION_STATUS_SUCCESS, PAYMENT_PERIOD_ANUALY, PAYMENT_PERIOD_DAILY, PAYMENT_PERIOD_MONTHLY, PRODUCT_NAME_BASIC, PRODUCT_NAME_COORPORATE, PRODUCT_NAME_PLUS, PRODUCT_NAME_PREMIUM, PRUDUCT_TYPE_ADESAO, PRUDUCT_TYPE_CONVERSA_AVULSA, PRUDUCT_TYPE_PLAN, SEM_METODO_DE_PAGAMENTO_CLIENTE_LOCALIZADO_NA_CONVERSA, SLEEP_SECONDS_INTER_AI_API_CALL, STATUS_CONVERSA_EM_ANDAMENTO, STATUS_CONVERSA_ENCERRADA, STATUS_CONVERSA_FALHA, STATUS_PEDIDO_CANCELADO, STATUS_PEDIDO_EM_PROCESSO, STATUS_PEDIDO_ENTREGUE, STATUS_PEDIDO_PENDENTE_DE_ENTREGA, STATUS_PEDIDO_REALIZADO, USER_LEVEL_FREE, USER_LEVEL_PREMIUM, USER_PAYMENT_METHOD_FAILED, USER_PAYMENT_METHOD_NOT_REGISTERED, USER_PAYMENT_METHOD_STATUS_OK

sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
def current_date_sao_paulo():
    return datetime.now().astimezone(sao_paulo_tz).date()
def current_time_sao_paulo():
    return datetime.now().astimezone(sao_paulo_tz).time()

phone_regex = RegexValidator(
    regex=r'^\d{10,11}$',
    message="Favor digitar seu telefone da seguinte forma: seu DDD seguido do seu número, por exemplo: 11987654321"
)

class CustomUser(AbstractUser):

    USER_LEVEL_CHOICES = (
        (USER_LEVEL_FREE , 'Usuário em teste gratuito'),
        (USER_LEVEL_PREMIUM , 'Usuário Premium'),
        )
    
    USER_USAGE_PAYMENT_METHOD_CHOICES = (
        (USER_PAYMENT_METHOD_NOT_REGISTERED, 'Método de pagamento ainda não registrado'),
        (USER_PAYMENT_METHOD_STATUS_OK, 'Método de pagamento registrado'),
        (USER_PAYMENT_METHOD_FAILED, 'Método de pagamento falhou'),
    )
    
    groups = models.ManyToManyField(Group, blank=True, related_name="%(app_label)s_%(class)s_related")
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name="%(app_label)s_%(class)s_related")

    email_confirmed = models.BooleanField(default=False)
    email_confirmation_token = models.CharField(max_length=200, blank=True, null=True)

    full_name = models.CharField(
        max_length=60,
        default='',
    )
    company_name = models.CharField(
        max_length=60,
        default='',
    )
    cell_phone = models.CharField(
        validators=[phone_regex],
        default='99999999999',
    )
    segmento = models.CharField(
        max_length=60,
        default='',
    )
    cargo_atual = models.CharField(
        max_length=60,
        default='',
    )

    user_plan = models.CharField(
        max_length=40,
        default=USER_LEVEL_FREE,
        choices=USER_LEVEL_CHOICES,
        )
    
    user_usage_payment_method_status = models.CharField(
        max_length=40,
        default=USER_PAYMENT_METHOD_NOT_REGISTERED,
        choices=USER_USAGE_PAYMENT_METHOD_CHOICES,
        )
    

    last_payment_date = models.DateField(null=True, blank=True)
    stripe_id = models.CharField(max_length=50, blank=True, null=True)
    conversation_limit_set_by_user = models.DecimalField(
        max_digits=7, 
        decimal_places=2, 
        default=5000.00
        )
    limit_on=models.BooleanField(default=False)
    valor_em_debito = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00
        )
    
    chatbots_on = models.BooleanField(default=True)

    def usuario_adimplente(self):
        if self.valor_em_debito > 0:
            return False
        return True
    
    def usuario_adimplente_ou_tolerancia_de_uso(self):
        if not self.usuario_adimplente:
            if self.last_payment_date is not None:
                today = timezone.now().astimezone(sao_paulo_tz).date()
                max_tolerance_day = self.last_payment_date + timedelta(days=DIAS_TOLERACIA_INADIMPLECIA)
                if today > max_tolerance_day:
                    return False
        return True
    
    def userIsPremium(self):
        if self.user_plan == USER_LEVEL_PREMIUM:
            return True
        return False

    @staticmethod
    def getUser(request):
        if request.user.is_authenticated:
            return CustomUser.objects.get(id=request.user.id)
        return None
    
    
    def generate_confirmation_token(self):
        """
        Generates a unique email confirmation token
        """
        token_generator = PasswordResetTokenGenerator()  #uses password reset token generetor, but it is inted to serve as a token to email confirmation
        token = token_generator.make_token(self)
        self.email_confirmation_token = token
        self.save()
        return token
    
    def confirm_email(self, token):
        """
        Marks the user's email as confirmed if the given token is valid
        """
        token_generator = PasswordResetTokenGenerator()
        if token_generator.check_token(self, token):
            self.email_confirmed = True
            self.email_confirmation_token = None
            self.save()
            return True
        else:
            return False
        
    @staticmethod
    def register_and_login_new_user(form, request):
        from ajudai_django_app.forms import USER_NAME_FIELD_ID
        # crie um novo usuário
        user = form.save(commit=False)
        user.email_confirmed = False
        user.generate_confirmation_token()
        user.save()
        #loga o usuário na conta antes de direcioná-lo para home:
        username = form.cleaned_data.get(USER_NAME_FIELD_ID)
        password = form.cleaned_data.get('password1')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)

    def is_payment_time(self, reset_period):
        if self.user_plan == USER_LEVEL_FREE:
            return False
        
        today = timezone.now().astimezone(sao_paulo_tz).date()

        #usuário recém aderido como premium
        #o caso do last_payment_date ser None é do usuário que acabou de se tornar premium. Neste caso, ele é setado no dia atual, para que o pagamento devido fique para daqui um período
        if self.last_payment_date is None:
            self.last_payment_date = today
            return False
        
        if reset_period == PAYMENT_PERIOD_DAILY:
            reset_date = self.last_payment_date + timedelta(days=1)
        elif reset_period == PAYMENT_PERIOD_MONTHLY:
            year, month = self.last_payment_date.year, self.last_payment_date.month + 1
            day =self.last_payment_date.day
            if month > 12:
                year += 1
                month = 1
            reset_date = self.last_payment_date.replace(year=year, month=month, day=day)
        elif reset_period == PAYMENT_PERIOD_ANUALY:
            year = self.last_payment_date.year + 1
            month = self.last_payment_date.month
            day =self.last_payment_date.day
            reset_date = self.last_payment_date.replace(year=year, month=month, day=day)
        else:
            raise ValueError('Invalid reset period')

        if today >= reset_date:
            return True
        return False
    
    def days_to_next_payment(self, reset_period):
        if self.user_plan == USER_LEVEL_FREE:
            return None
        
        today = timezone.now().astimezone(sao_paulo_tz).date()

        if self.last_payment_date is None:
            self.last_payment_date = today
        
        if reset_period == PAYMENT_PERIOD_DAILY:
            reset_date = self.last_payment_date + timedelta(days=1)
        elif reset_period == PAYMENT_PERIOD_MONTHLY:
            year, month = self.last_payment_date.year, self.last_payment_date.month + 1
            day =self.last_payment_date.day
            if month > 12:
                year += 1
                month = 1
            reset_date = self.last_payment_date.replace(year=year, month=month, day=day)
        elif reset_period == PAYMENT_PERIOD_ANUALY:
            year = self.last_payment_date.year + 1
            month = self.last_payment_date.month
            day =self.last_payment_date.day
            reset_date = self.last_payment_date.replace(year=year, month=month, day=day)

        return (reset_date - today).days

        
    def reset_payment_date(self, reset_period):
        if self.userIsPremium == True:
            today = timezone.now().astimezone(sao_paulo_tz).date()
            if reset_period == PAYMENT_PERIOD_DAILY:
                reset_date = self.last_payment_date + timedelta(days=1)
            elif reset_period == PAYMENT_PERIOD_MONTHLY:
                # Get the next month
                year, month = self.last_payment_date.year, self.last_payment_date.month + 1
                day =self.last_payment_date.day
                if month > 12:
                    year += 1
                    month = 1
                reset_date = self.last_payment_date.replace(year=year, month=month, day=day)
            elif reset_period == PAYMENT_PERIOD_ANUALY:
                # Get the next month
                year = self.last_payment_date.year + 1
                month = self.last_payment_date.month
                day =self.last_payment_date.day
                reset_date = self.last_payment_date.replace(year=year, month=month, day=day)
            else:
                raise ValueError('Invalid reset period')

            if today >= reset_date:
                self.last_payment_date = today
                self.save()

    def atualiza_valor_em_debito(self, valor_a_adicionar):
        valor_devido_anterior = self.valor_em_debito
        self.valor_em_debito = valor_devido_anterior + valor_a_adicionar
        self.save()
    
    def current_user_plan_price_and_conversas_a_pagar(self, reset_period):
        if self.userIsPremium == False:
            return None, None, None
        self.reset_payment_date(reset_period)
        conversas_a_pagar = Conversa.count_conversations_in_current_billing_period(self)
        product = Product.objects.filter(Q(minimo_conversas__lte=conversas_a_pagar) & Q(maximo_conversas__gte=conversas_a_pagar)).first()
        price = None
        if product:
            price = product.price_shown

        return product, price, conversas_a_pagar

    def charge_new_conversations_first_attempt(self, reset_period):
        product, price, conversas_a_pagar = self.current_user_plan_price_and_conversas_a_pagar(reset_period)
        total_cost = price * conversas_a_pagar
        charge_usages(total_cost, self)
        #TODO VER SE ABAIXO ESTA CORRETO E TESTAR
        nova_fatura = PaymentsForUseMadde.objects.create(
            user = self,
            numero_conversas = conversas_a_pagar,
            product_name = product.name,
            product_price = product.price_shown,
            valor_total='R$'+str(total_cost),
            date=current_date_sao_paulo,
            time=current_time_sao_paulo,
            )
        self.atualiza_valor_em_debito(total_cost)

    def inform_all_user_debt(self):
        return self.valor_em_debito
    
    def charge_all_user_debt(self):
        total_cost = self.valor_em_debito
        charge_usages(total_cost, self)

    def finance_check(self, reset_period):
        if self.is_payment_time(reset_period):
            self.reset_payment_date(reset_period)
            #cobra cnversas aguardando vencimento
            self.charge_new_conversations_first_attempt(reset_period)
            #transforma as conversas que aguardam vencimento em conversas em divida (elas serao transformadas em regulares apos o webhook)
            Conversa.conversations_to_payment_due(self)

    def reduce_debt_amount(self, amount_payed):
        self.valor_em_debito = 0
        self.save()

        #TODO VARIFICAR NECESSIDADE DE REFINAR MÉTODO DESCONTANDO SO O AMOUNT_PAYED
        '''
        valor_devido_anterior = self.valor_em_debito
        valor_devido_atual = valor_devido_anterior - amount_payed
        if valor_devido_atual >=0:
            self.valor_em_debito = valor_devido_atual
        else:
            self.valor_em_debito = 0
        self.save()
        '''

    def can_create_new_messages(self, reset_period):
        if self.is_payment_time(reset_period):
            self.reset_payment_date(reset_period)
            Conversa.conversations_to_payment_due(self)
            conversas_a_pagar = Conversa.count_pending_payment_conversations(self)
            if self.limit_on:
                if conversas_a_pagar>self.conversation_limit_set_by_user:
                    return False
                ''' DESATIVADO POR LIMITE AGORA EH DE CONVERSAS
                product = Product.objects.filter(Q(minimo_conversas__lte=conversas_a_pagar) & Q(maximo_conversas__gte=conversas_a_pagar)).first()
                if product:
                    price = product.price_shown
                    total_cost = price * conversas_a_pagar
                    if total_cost >= self.moneatry_limit_set_by_user:
                        return False
                '''

        return True      
    
    def total_conversas(self):
        chatbots = ChatBot.objects.filter(user=self)
        total_conversas = Conversa.objects.filter(chatbot__in=chatbots).count()
        return total_conversas  

class Premium_User_Payment_Method_Registration(models.Model):
    PREMIUM_USER_REGISTER_STATUS_CHOICES = (
        PAYMENT_METHOD_REGISTRATION_STATUS_PENDING,
        PAYMENT_METHOD_REGISTRATION_STATUS_SUCCESS,
    )
    STATUS_CHOICES=(
        (PAYMENT_METHOD_REGISTRATION_STATUS_PENDING, 'Pending Payment Method'),
        (PAYMENT_METHOD_REGISTRATION_STATUS_SUCCESS, 'Approved Payment Method'),
        (PAYMENT_METHOD_REGISTRATION_STATUS_FAILING, 'Rejected Paging Method. Please change it to continue using the services'),
    )

    id = models.AutoField(primary_key=True)
    date = models.DateField(default=current_date_sao_paulo)
    time = models.TimeField(default=current_time_sao_paulo)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, default=1)
    stripe_checkout_id = models.CharField(max_length=255, default='')
    status = models.CharField(
        max_length=50, 
        default=PAYMENT_METHOD_REGISTRATION_STATUS_PENDING,
        choices=STATUS_CHOICES,
        )

    def register_confirm_payment_method(self):
        self.status = PAYMENT_METHOD_REGISTRATION_STATUS_SUCCESS
        self.save()

    def payment_method_not_working(self):
        self.status = PAYMENT_METHOD_REGISTRATION_STATUS_FAILING
        self.save()
        
#produto (método de cobrança) são por conversas finalizadas por um modelo de ia
class Product(models.Model):
    AI_API_PROVIDERS_CHOICES = (
        (AI_PROVIDER_OPEN_AI , 'Open AI'),
        )
    AI_MODEL_CHOICES = (
        (GPT3_MODEL_NAME, 'GPT 3.5'),
        )
    CURRENCY_CHOICES = (
        (BRL_CURRENCY_SIMBOL, 'Reais (R$)'),
    )
    PRODUCT_TYPES = (
        (PRUDUCT_TYPE_ADESAO , 'Adesão'),
        (PRUDUCT_TYPE_CONVERSA_AVULSA , 'Conversa Aulsa'),
    )
    PRODUCT_NAME_CHOICES = (
        (PRODUCT_NAME_BASIC, 'Basic'),
        (PRODUCT_NAME_PLUS, 'Plus'),
        (PRODUCT_NAME_PREMIUM, 'Premium'),
        (PRODUCT_NAME_COORPORATE, 'Corporativo VIP'),
    )

    name = models.CharField(
        max_length=32,
        default=PRODUCT_NAME_BASIC,
        choices=PRODUCT_NAME_CHOICES,
        )
    tipo_de_produto = models.CharField(
        max_length=30,
        default=PRUDUCT_TYPE_CONVERSA_AVULSA,
        choices=PRODUCT_TYPES,
        )
    ai_api_provider  = models.CharField(
        max_length=120,
        default='',
        choices=AI_API_PROVIDERS_CHOICES,
        )
    ai_model_name = models.CharField(
        max_length=120,
        default='',
        choices=AI_MODEL_CHOICES,
        )
    free_use_limit_conversations = models.PositiveIntegerField(
        default=0,
        )
    priceID = models.CharField(max_length=120,default='')
    currency = models.CharField(
        max_length=3, 
        choices=CURRENCY_CHOICES,
        default=BRL_CURRENCY_SIMBOL,
        )
    price_shown = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    minimo_conversas = models.PositiveIntegerField(default=0)
    maximo_conversas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    

class Adesao_Purchase(models.Model):
    PAYMENT_METHOD_CHOICES = (
        (PAYMENT_METHOD_CREDIT_CARD, 'Cartão de Crédito'),
        (PAYMENT_METHOD_BOLETO, 'Boleto'),
        (PAYMENT_METHOD_PIX, 'Pix'),
        (PAYMENT_METHOD_OTHER, 'Outro'),
    )


    id = models.AutoField(primary_key=True)
    date = models.DateField()
    time = models.TimeField(default=current_time_sao_paulo)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    stripe_checkout_id = models.CharField(max_length=255, default='')
    status = models.CharField(max_length=50, default=ADESAO_PURCHASE_STATUS_PENDING)
    payment_method = models.CharField(
        max_length=30, 
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_METHOD_CREDIT_CARD,
        )

    def cancel_purchase(self):
        self.status = ADESAO_PURCHASE_STATUS_CALCELED
        self.save()

class ChatBot(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    nome_do_chatbot = models.CharField(max_length=40, default='sem nome')
    aditional_intructions = models.CharField(max_length=MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, default='')
    cardapio = models.CharField(max_length=MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, default='')
    descricao_funcao_cardapio = models.CharField(max_length=1000, default='Obtém uma informação específica, ou um conjunto de informações específicas contidas no cardápio, como nome do produto, tamanho, ingredientes e preço')
    whatsapp_number=models.CharField(
        validators=[phone_regex],
        default='99999999999',
    )
    whats_app_api_auth_token = models.CharField(max_length=300)
    facebook_page_id = models.CharField(max_length=120)
    creation_date = models.DateField(default=current_date_sao_paulo)
    creation_time = models.TimeField(default=current_time_sao_paulo)

    def __str__(self):
        name = self.nome_do_chatbot
        return f"ChatBot {name}"

#o uso é considerado como uma conversa inteira finalizada
class Conversa(models.Model):

    STATUS_CHOICES = (
        (STATUS_CONVERSA_EM_ANDAMENTO , 'Conversa em andamento'),
        (STATUS_CONVERSA_ENCERRADA , 'Conversa encerrada'),
        (STATUS_CONVERSA_FALHA , 'Conversa encerrada (falha)'), # CONVERSA NÃO COBRADA
        )
    FINANCEIRO_CHOICES = (
        (CONVERSA_PAGA, 'Conversa Paga'),
        (CONVERSA_PAGAMENTO_PENDENTE, 'Pagamento Pendente'), #conversa já vencida mas não paga
        (CONVERSA_AGUARDANDO_VENCIMENTO, 'Conversa Aguardando Vencimento Para Ser Cobrada'),
    )
    
    id = models.AutoField(primary_key=True)

    creation_date = models.DateField(default=current_date_sao_paulo)
    creation_time = models.TimeField(default=current_time_sao_paulo)

    #date and time registram momento da ultima mensagem
    date = models.DateField(default=current_date_sao_paulo)
    time = models.TimeField(default=current_time_sao_paulo)
    # o set null abaixo proteje a conversa em caso do cliente deletar o chatbot, dado que a conversa é usada para cobrança
    chatbot = models.ForeignKey(ChatBot, on_delete=models.SET_NULL, null=True)
    context = models.JSONField(default=list) #o default numa conversa recem criado é uma lista vazia
    messages_display_time = models.JSONField(default=list)
    company_client_number  = models.CharField(max_length=20) #numero de quem está mandando a mensagem para o bot (NÃO O NÚMERO DO DONO DO BOT)
    total_tokens_used = models.PositiveIntegerField(
        default=0,
        )
    total_messages_sent = models.PositiveIntegerField(
        default=0,
        )
    numero_do_pedido_gerado_com_a_conversa = models.PositiveIntegerField(
        default=0,
        )
    status_da_conversa = models.CharField(
        max_length=120,
        default=STATUS_CONVERSA_EM_ANDAMENTO,
        choices=STATUS_CHOICES,
        )
    financial_status =  models.CharField(
        max_length=70,
        default=CONVERSA_AGUARDANDO_VENCIMENTO,
        choices=FINANCEIRO_CHOICES,
        )
    chatbot_ativo = models.BooleanField(default=True)
    last_message_shown = models.BooleanField(default=False)
    need_refresh_view = models.BooleanField(default=False)
    
    def add_message_to_conversa(self, message_text, role):
        context = self.context
        messages_time = self.messages_display_time

        context.append({"role": role, "content": message_text})

        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        now = timezone.now().astimezone(sao_paulo_tz)

        date_str = now.date().strftime('%d/%m/%Y')
        time_str = now.time().strftime('%H:%M')


        messages_time.append({"date": date_str, "time": time_str})

        self.save()

    def substitute_conversa_context(self, new_context):
    
        self.context = new_context

        if len(new_context) > len(self.messages_display_time):
            num_new_messages = len(new_context) - len(self.messages_display_time)

            # Set the timezone to São Paulo
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
            now = timezone.now().astimezone(sao_paulo_tz)

            date_str = now.date().strftime('%d/%m/%Y')
            time_str = now.time().strftime('%H:%M')

            for _ in range(num_new_messages):
                self.messages_display_time.append({"date": date_str, "time": time_str})

        self.save()

    @staticmethod
    def conversations_to_payment_due(user):
        user_chatbots = ChatBot.objects.filter(user=user)
        waiting_due_conversations = Conversa.objects.filter(Q(chatbot__in=user_chatbots) & Q(financial_status=CONVERSA_AGUARDANDO_VENCIMENTO))
        for conversation in waiting_due_conversations:
            conversation.financial_status = CONVERSA_PAGAMENTO_PENDENTE
            conversation.save()

    @staticmethod
    def count_pending_payment_conversations(user):
        user_chatbots = ChatBot.objects.filter(user=user)
        pending_conversations = Conversa.objects.filter(Q(chatbot__in=user_chatbots) & Q(financial_status=CONVERSA_PAGAMENTO_PENDENTE))
        return pending_conversations.count()
    
    @staticmethod
    def count_conversations_in_current_billing_period(user):
        user_chatbots = ChatBot.objects.filter(user=user)
        current_conversations = Conversa.objects.filter(Q(chatbot__in=user_chatbots) & Q(financial_status=CONVERSA_AGUARDANDO_VENCIMENTO))
        return current_conversations.count()


    @staticmethod
    def register_payed_conversations(user, amount_payed):
        user_chatbots = ChatBot.objects.filter(user=user)
        pending_conversations = Conversa.objects.filter(Q(chatbot__in=user_chatbots) & Q(financial_status=CONVERSA_PAGAMENTO_PENDENTE))
        #TODO VARIFICAR NECESSIDADE DE REFINAR MÉTODO PARA APENAS CONVERTER AS CONVERSAS NO LIMITE DO AMOUNT PAYED
        for conversation in pending_conversations:
            conversation.financial_status = CONVERSA_PAGA
            conversation.save()

    @staticmethod
    def close_conversa_if_needed(user):
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        now = timezone.now().astimezone(sao_paulo_tz)

        conversations = Conversa.objects.filter(chatbot__user=user, status_da_conversa=STATUS_CONVERSA_EM_ANDAMENTO)

        for conversation in conversations:
            last_message_datetime = timezone.make_aware(datetime.combine(conversation.date, conversation.time))
            creation_datetime = timezone.make_aware(datetime.combine(conversation.creation_date, conversation.creation_time))
            
            if (now - last_message_datetime) > timedelta(hours=HOURS_TO_RESET_INACTIVE):
                conversation.status_da_conversa = STATUS_CONVERSA_ENCERRADA
                send_response(conversation.chatbot.facebook_page_id, conversation.chatbot.whats_app_api_auth_token, conversation.company_client_number, MENSAGEM_ENCERRAMENTO_DE_CONVERSA_INATIVIDADE)
                conversation.update_conversa_time_date()
                conversation.add_message_to_conversa(MENSAGEM_ENCERRAMENTO_DE_CONVERSA_INATIVIDADE, "assistant")
                conversation.save()
                
                continue
            
            if (now - creation_datetime) > timedelta(hours=HOURS_TO_RESER_ABSOLUTE):
                conversation.status_da_conversa = STATUS_CONVERSA_ENCERRADA
                send_response(conversation.chatbot.facebook_page_id, conversation.chatbot.whats_app_api_auth_token, conversation.company_client_number, MENSAGEM_ENCERRAMENTO_DE_CONVERSA_INATIVIDADE)
                conversation.update_conversa_time_date()
                conversation.add_message_to_conversa(MENSAGEM_ENCERRAMENTO_DE_CONVERSA_TEMPO_LIMITE, "assistant")
                conversation.save()
    
    def update_conversa_time_date(self):
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        self.date = timezone.now().astimezone(sao_paulo_tz).date()
        self.time = timezone.now().astimezone(sao_paulo_tz).time()
        self.save()

    def __str__(self):
        conversa_id = self.id
        return f"Conversa n° {conversa_id} - com o número: {self.company_client_number} - status: {self.status_da_conversa}"

class DadosClienteCadatrado(models.Model):

    ultima_conversa = models.ForeignKey(Conversa, on_delete=models.SET_NULL, null=True)
    nome = models.CharField(
        max_length=60,
        default='',
    )
    endereco = models.CharField(
        max_length=60,
        default='',
    )
    telefone = models.CharField(
        max_length=20,
        default='',
        )
    metodo_pagamento = models.CharField(
        max_length=60,
        default='',
    )
    
    def __str__(self):
        return self.nome

class Pedido(models.Model):
    STATUS_CHOICES = (
        (STATUS_PEDIDO_REALIZADO , 'Pendido realizado'),
        (STATUS_PEDIDO_EM_PROCESSO , 'Pedido em processo'),
        (STATUS_PEDIDO_PENDENTE_DE_ENTREGA , 'Pendente de Entrega'),
        (STATUS_PEDIDO_ENTREGUE , 'Pedido Entregue'),
        (STATUS_PEDIDO_CANCELADO , 'Pedido Cancelado'),
        )
    

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    criado_manualmente = models.BooleanField(default=False)
    nome_pedido_manual = models.CharField(
        max_length=120,
        default='',
        )
    conversa = models.ForeignKey(Conversa, on_delete=models.SET_NULL, null=True)
    status_do_pedido = models.CharField(
        max_length=120,
        default=STATUS_PEDIDO_REALIZADO,
        choices=STATUS_CHOICES,
        )
    resumo_do_pedido = models.CharField(
        default='',
        )
    date = models.DateField(default=current_date_sao_paulo)
    time = models.TimeField(default=current_time_sao_paulo)
    nome_do_cliente = models.CharField(
        max_length=60,
        default='',
        )
    itens_pedido = models.CharField(
        max_length=12000,
        default=''
        )
    endereco_entrega=models.CharField(
        max_length=200,
        default='',
        )
    taxa_de_entrega = models.CharField(
        max_length=60,
        default='',
        )
    valor_total = models.CharField(
        max_length=60,
        default='',
        )


    def mensagem_novo_status(self):
        mensagem = ' '
        if self.status_do_pedido == STATUS_PEDIDO_REALIZADO:
            mensagem = 'Atenção, seu pedido foi realizado e será processado!'
        if self.status_do_pedido == STATUS_PEDIDO_EM_PROCESSO:
            mensagem = 'Atenção, seu pedido está sendo processado!'
        if self.status_do_pedido == STATUS_PEDIDO_PENDENTE_DE_ENTREGA:
            mensagem = 'Atenção, seu pedido já saiu para a entrega!'
        if self.status_do_pedido == STATUS_PEDIDO_ENTREGUE:
            mensagem = 'Atenção, seu pedido foi entregue! Aproveite!'
        return mensagem
    
    def extrair_valor_total_pedido_do_resumo(self):
        """
        pattern = r'R\$ *[\d\.]*\,\d\d'
        matches = re.findall(pattern, self.resumo_do_pedido)  # This finds all instances of the pattern

        total_pedido = Decimal('0.00')  # initialize the total order value
        for match in matches:
            # Remove the 'R$' and replace the comma with a dot to convert to a Decimal
            value = Decimal(match.replace('R$', '').replace(',', '.'))
            total_pedido += value

        return total_pedido
        """
        try:
            return ai_gpt_extrair_dado_do_resumo('valor da total do pedido (colocar R$ na frente do valor)' ,self.resumo_do_pedido)
        except:
            return 'Não foi possível extrair o total do pedido da conversa'
        
    def extrair_metodo_pagamento_do_resumo(self):
        try:
            return ai_gpt_extrair_dado_do_resumo('método de pagamento' ,self.resumo_do_pedido)
        except:
            return "Não foi possível extrair o método de pagamento da conversa"
    
    def extrair_endereco_cliente_do_resumo(self):
        try:
            return ai_gpt_extrair_endereco_do_resumo(self.resumo_do_pedido)
        except:
            return "Não foi possível extrair o endereço de entrega da conversa"
    
    def extrair_nome_cliente_do_resumo(self):
        try:
            return ai_gpt_extrair_dado_do_resumo('nome do cliente' ,self.resumo_do_pedido)
        except:
            return 'Não foi possível extrair o nome do cliente da conversa'
    
    def extrair_itens_do_pedido_do_resumo(self):
        try:
            return ai_gpt_extrair_dado_do_resumo('itens do pedido, incluindo o item, quantidade (1x, 2x, 3x...) e preço do item' ,self.resumo_do_pedido)
        except:
            return 'Não foi possível extrair o nome do cliente da conversa'
        
    def extrair_taxa_de_entrega_do_pedido_do_resumo(self):
        try:
            return ai_gpt_extrair_dado_do_resumo('valor da taxa de entrega' ,self.resumo_do_pedido)
        except:
            return 'Não foi possível extrair a taxa de entrega da conversa'

    # ciração de pedido a ser chamada quando não se tem os parâmetros do pedido (a serem extraidos do reumo)
    @staticmethod
    def criar_novo_pedido(user, conversation, resumo, numero_cliente):
        pedido = Pedido.objects.create(
            user=user,
            conversa=conversation,
            resumo_do_pedido = resumo,
        )
        attempt_count = 0
        success_pedido_register = False
        while attempt_count < API_MAX_ATTEMP and success_pedido_register == False:
            try:
                time.sleep(SLEEP_SECONDS_INTER_AI_API_CALL)
                nome_cliente = pedido.extrair_nome_cliente_do_resumo()
                time.sleep(SLEEP_SECONDS_INTER_AI_API_CALL)
                endereco_cliente = pedido.extrair_endereco_cliente_do_resumo()
                time.sleep(SLEEP_SECONDS_INTER_AI_API_CALL)
                valor_total = pedido.extrair_valor_total_pedido_do_resumo()
                time.sleep(SLEEP_SECONDS_INTER_AI_API_CALL)
                itens_pedido = pedido.extrair_itens_do_pedido_do_resumo()
                pedido.nome_do_cliente = nome_cliente
                pedido.endereco_entrega=endereco_cliente
                pedido.valor_total=valor_total
                pedido.itens_pedido = itens_pedido
                pedido.save()
                success_pedido_register = True
            except:
                 time.sleep(SLEEP_SECONDS_INTER_AI_API_CALL)

                                    #se os dados do cliente do pedido ja existem, atualiza-os
        try:
            dados_cliente = DadosClienteCadatrado.objects.get(
                 ultima_conversa__company_client_number=conversation.company_client_number)
            # If the object is found, update the fields
            dados_cliente.ultima_conversa = conversation
            dados_cliente.nome = nome_cliente
            dados_cliente.endereco = endereco_cliente
            dados_cliente.metodo_pagamento = pedido.extrair_metodo_pagamento_do_resumo()
            dados_cliente.save()
        #se os dados do cliente ainda nao existem, cria-se novo objeto
        except ObjectDoesNotExist:
            dados_cliente = DadosClienteCadatrado.objects.create(
                ultima_conversa=conversation,
                nome=nome_cliente,
                endereco=endereco_cliente,
                metodo_pagamento = pedido.extrair_metodo_pagamento_do_resumo(),
                telefone = numero_cliente,
            )

    def criar_novo_pedido_ja_com_parametros(nome_cliente, endereco_cliente, itens_pedido, taxa_de_entrega, valor_total, metodo_de_pagamento, resumo_do_pedido, user, conversation):
        pedido = Pedido.objects.create(
            user=user,
            conversa=conversation,
            resumo_do_pedido = resumo_do_pedido,
        )

        pedido.nome_do_cliente = nome_cliente
        pedido.endereco_entrega=endereco_cliente
        pedido.valor_total=valor_total
        pedido.itens_pedido = itens_pedido
        pedido.taxa_de_entrega = taxa_de_entrega
        pedido.save()

        try:
            dados_cliente = DadosClienteCadatrado.objects.get(
                 ultima_conversa__company_client_number=conversation.company_client_number)
            # If the object is found, update the fields
            dados_cliente.ultima_conversa = conversation
            dados_cliente.nome = nome_cliente
            dados_cliente.endereco = endereco_cliente
            dados_cliente.metodo_pagamento = metodo_de_pagamento
            dados_cliente.save()
        #se os dados do cliente ainda nao existem, cria-se novo objeto
        except ObjectDoesNotExist:
            dados_cliente = DadosClienteCadatrado.objects.create(
                ultima_conversa=conversation,
                nome=nome_cliente,
                endereco=endereco_cliente,
                metodo_pagamento = metodo_de_pagamento,
                telefone = conversation.company_client_number,
            )
    
    def __str__(self):
        if self.criado_manualmente == True:
            return self.nome_pedido_manual
        
        return f"Pedido {self.id}"


class PaymentsForUseMadde(models.Model):
    FINANCEIRO_CHOICES = (
        (FATURA_PAGA, 'Pagamnento confirmado'),
        (FATURA_PENDENTE, 'Aguardando confirmação'), #conversas já vencidas mas não pagas
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(default=current_date_sao_paulo)
    time = models.TimeField(default=current_time_sao_paulo)
    product_name = models.CharField(
        max_length=120,
        default=PRODUCT_NAME_BASIC,
        )
    product_price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=120,
        default=FATURA_PENDENTE,
        choices=FINANCEIRO_CHOICES,
        )
    numero_conversas = models.PositiveIntegerField(
        default=0,
        )
    valor_total = models.CharField(
        max_length=20,
        default='R$0,00',
        )
    
    @staticmethod
    def registrar_fatura_paga(user):
        user_payments = PaymentsForUseMadde.objects.filter(user=user)
        for payment in user_payments:
            payment.status = FATURA_PAGA
            FATURA_PAGA.save()
        #TODO AVALIAR REFINAMENTO PARA SÓ SER PAGO O VALOR RECEBIDO NO WEBHOOK
        #TODO FALTA TESTE

def register_adesao_purchase_after_webhook_confirm(checkout_id):
    try:
        #garantindo que a operação seja realizada inteiramente, ou não executada 
        with transaction.atomic():
            purchase = Adesao_Purchase.objects.get(stripe_checkout_id=checkout_id)
            user = CustomUser.objects.get(id=purchase.user.id)

            purchase.status = ADESAO_PURCHASE_STATUS_PROCESSED
            purchase.time = timezone.datetime.now().time()
            purchase.date = timezone.datetime.now().date()
            purchase.save()

            user.user_plan = USER_LEVEL_PREMIUM
            user.save()
    except Exception as e:
        print(f'Error while processing payment: {e}')

def register_payment_method_success_after_webhook_confirm(checkout_id):
    try:
        #garantindo que a operação seja realizada inteiramente, ou não executada 
        with transaction.atomic():
            payment_method = Premium_User_Payment_Method_Registration.objects.get(stripe_checkout_id=checkout_id)
            user = CustomUser.objects.get(id=payment_method.user.id)

            payment_method.status = PAYMENT_METHOD_REGISTRATION_STATUS_SUCCESS
            payment_method.time = timezone.datetime.now().time()
            payment_method.date = timezone.datetime.now().date()
            payment_method.save()

            user.user_usage_payment_method_status = USER_PAYMENT_METHOD_STATUS_OK
            user.save()
    except Exception as e:
        print(f'Error while processing payment: {e}')


#método para corrigir eventual distorção de ausência de informação nohorário de mensgaens
def update_conversa_objects():
    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
    now = timezone.now().astimezone(sao_paulo_tz)

    date_str = now.date().strftime('%d/%m/%Y')
    time_str = now.time().strftime('%H:%M')

    for conversa in Conversa.objects.all():
        if len(conversa.context) > len(conversa.messages_display_time):
            num_new_messages = len(conversa.context) - len(conversa.messages_display_time)

            for _ in range(num_new_messages):
                conversa.messages_display_time.append({"date": date_str, "time": time_str})

        conversa.save()