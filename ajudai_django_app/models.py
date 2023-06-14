from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import Group, Permission
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta, datetime

from constants import ADESAO_PURCHASE_STATUS_CALCELED, ADESAO_PURCHASE_STATUS_PENDING, ADESAO_PURCHASE_STATUS_PROCESSED, AI_PROVIDER_OPEN_AI, BRL_CURRENCY_SIMBOL, CONVERSA_AGUARDANDO_VENCIMENTO, CONVERSA_PAGA, CONVERSA_PAGAMENTO_PENDENTE, GPT3_MODEL_NAME, MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, PAYMENT_METHOD_REGISTRATION_STATUS_FAILING, PAYMENT_METHOD_REGISTRATION_STATUS_PENDING, PAYMENT_METHOD_REGISTRATION_STATUS_SUCCESS, PAYMENT_PERIOD_ANUALY, PAYMENT_PERIOD_DAILY, PAYMENT_PERIOD_MONTHLY, PRUDUCT_TYPE_ADESAO, PRUDUCT_TYPE_CONVERSA_AVULSA, PRUDUCT_TYPE_PLAN, STATUS_CONVERSA_EM_ANDAMENTO, STATUS_CONVERSA_FALHA, STATUS_CONVERSA_PEDIDO_REALIZADO, STATUS_PEDIDO_CANCELADO, STATUS_PEDIDO_ENTREGUE, STATUS_PEDIDO_PENDENTE_DE_ENTREGA, USER_LEVEL_FREE, USER_LEVEL_PREMIUM, USER_PAYMENT_METHOD_FAILED, USER_PAYMENT_METHOD_NOT_REGISTERED, USER_PAYMENT_METHOD_STATUS_OK

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

    moneatry_limit_set_by_user = models.DecimalField(
        max_digits=7, 
        decimal_places=2, 
        default=5000.00
        )

    def usuario_adimplente(self):
        #TODO verificar se o dia atual ainda está comprendido na data de ultimo pagamento mais periodo de renovação
        #TODO chamada de função em começos de view com verificação de usuário para 
        return True
    
    def usuario_adimplente_ou_tolerancia_de_uso(self):
        #TODO
        return True

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
        
        today = timezone.now().date()

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
        
    def reset_payment_date(self, reset_period):
        today = timezone.now().date()
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

    def regular_charge_user_if_needed(self, reset_period):
        if self.is_payment_time(reset_period):
            #TODO CALCULAR VALOR DEVIDO, ATRVES DE CONVERSAS MARCADAS COMO CONVERSA_AGUARDANDO_VENCIMENTO (PODE SER ATRAVÉS DE UM MÉTODO EM CONVERSAS)
            #TODO CHAMAR FUNÇÃO DE COBRANÇA
            self.reset_payment_date(reset_period)

    def charge_user_on_debt(self):
        #TODO CALCULAR VALOR DEVIDO ATRAVES DE CONVERSAS MARCADAS COMO CONVERSA_PAGAMENTO_PENDENTE (PODE SER ATRAVÉS DE UM MÉTODO EM CONVERSAS)
        #TODO CHAMAR FUNÇÃO DE COBRANÇA
        pass

class Premium_User_Payment_Method_Registration(models.Model):
    PREMIUM_USER_REGISTER_STATUS_CHOICES = (
        PAYMENT_METHOD_REGISTRATION_STATUS_PENDING,
        PAYMENT_METHOD_REGISTRATION_STATUS_SUCCESS,
    )
    STATUS_CHOICES=(
        (PAYMENT_METHOD_REGISTRATION_STATUS_PENDING, 'Pending Payment Method'),
        (PAYMENT_METHOD_REGISTRATION_STATUS_SUCCESS, 'Approved Payment Method'),
        (PAYMENT_METHOD_REGISTRATION_STATUS_PENDING, 'Rejected Paging Method. Please change it to continue using the services'),
    )

    id = models.AutoField(primary_key=True)
    date = models.DateField()
    time = models.TimeField(default=timezone.now)
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

    name = models.CharField(
        max_length=32,
        default='Conversa Finalizada',
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
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    time = models.TimeField(default=timezone.now)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    stripe_checkout_id = models.CharField(max_length=255, default='')
    status = models.CharField(max_length=50, default=ADESAO_PURCHASE_STATUS_PENDING)

    def cancel_purchase(self):
        self.status = ADESAO_PURCHASE_STATUS_CALCELED
        self.save()

class ChatBot(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    nome_do_chatbot = models.CharField(max_length=40, default='sem nome')
    aditional_intructions = models.CharField(max_length=MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, default='')
    whatsapp_number=models.CharField(
        validators=[phone_regex],
        default='99999999999',
    )
    whats_app_api_auth_token = models.CharField(max_length=300)
    facebook_page_id = models.CharField(max_length=120)
    creation_date = models.DateField(default=timezone.now)
    creation_time = models.TimeField(default=timezone.now)

    def __str__(self):
        name = self.nome_do_chatbot
        return f"ChatBot {name}"

#o uso é considerado como uma conversa inteira finalizada
class Conversa(models.Model):

    STATUS_CHOICES = (
        (STATUS_CONVERSA_EM_ANDAMENTO , 'Conversa em andamento'),
        (STATUS_CONVERSA_PEDIDO_REALIZADO , 'Conversa encerrada com pedido realizado'), # CONVERSA DEVE SER COBRADA
        (STATUS_CONVERSA_FALHA , 'Conversa encerrada por falha'), # CONVERSA NÃO COBRADA
        )
    FINANCEIRO_CHOICES = (
        (CONVERSA_PAGA, 'Conversa Paga'),
        (CONVERSA_PAGAMENTO_PENDENTE, 'Pagamento Pendente'), #conversa já vencida mas não paga
        (CONVERSA_AGUARDANDO_VENCIMENTO, 'Conversa Aguardando Vencimento Para Ser Cobrada'),
    )
    
    id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    # o set null abaixo proteje a conversa em caso do cliente deletar o chatbot, dado que a conversa é usada para cobrança
    chatbot = models.ForeignKey(ChatBot, on_delete=models.SET_NULL, null=True)
    context = models.JSONField(default=list) #o default numa conversa recem criado é uma lista vazia
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
    
    def __str__(self):
        conversa_id = self.id
        return f"Conversa n° {conversa_id} - com o número: {self.company_client_number} - status: {self.status_da_conversa}"
    
class Pedido(models.Model):
    STATUS_CHOICES = (
        (STATUS_PEDIDO_PENDENTE_DE_ENTREGA , 'Pendente de Entrega'),
        (STATUS_PEDIDO_ENTREGUE , 'Pedido Entregue'),
        (STATUS_PEDIDO_CANCELADO , 'Pedido Cancelado'),
        )
    

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    conversa = models.ForeignKey(Conversa, on_delete=models.SET_NULL, null=True)
    status_do_pedido = models.CharField(
        max_length=120,
        default=STATUS_PEDIDO_PENDENTE_DE_ENTREGA,
        choices=STATUS_CHOICES,
        )
    resumo_do_pedido = models.CharField(
        default='',
        )

    def __str__(self):
        return f"Pedido número {self.id}. Status: {self.status_do_pedido}"


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
            payment_method = Adesao_Purchase.objects.get(stripe_checkout_id=checkout_id)
            user = CustomUser.objects.get(id=payment_method.user.id)

            payment_method.status = PAYMENT_METHOD_REGISTRATION_STATUS_SUCCESS
            payment_method.time = timezone.datetime.now().time()
            payment_method.date = timezone.datetime.now().date()
            payment_method.save()

            user.user_usage_payment_method_status = USER_PAYMENT_METHOD_STATUS_OK
            user.save()
    except Exception as e:
        print(f'Error while processing payment: {e}')