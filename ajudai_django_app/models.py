from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import Group, Permission
from django.core.validators import RegexValidator
from django.utils import timezone

from constants import AI_PROVIDER_OPEN_AI, BRL_CURRENCY_SIMBOL, GPT3_MODEL_NAME, MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM

phone_regex = RegexValidator(
    regex=r'^\d{10,11}$',
    message="Favor digitar seu telefone da seguinte forma: seu DDD seguido do seu número"
)

class CustomUser(AbstractUser):
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

    name = models.CharField(
        max_length=32,
        default='Conversa Finalizada',
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
    capacity_level = models.CharField(
        max_length=32,
        default=''
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

    def __str__(self):
        return self.name

class ChatBot(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    aditional_intructions = models.CharField(max_length=MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, default='')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,)

    def __str__(self):
        chatot_id = self.id
        return f"ChatBot {chatot_id}"

#o uso é considerado como uma conversa inteira finalizada
class Conversa(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    date = models.DateField()
    time = models.TimeField(default=timezone.now)
    chatbot = models.ForeignKey(ChatBot, on_delete=models.CASCADE)
    total_tokens_used = models.PositiveIntegerField(
        default=0,
        )
    total_messages_sent = models.PositiveIntegerField(
        default=0,
        )
    numero_do_pedido_gerado_com_a_conversa = models.PositiveIntegerField(
        default=0,
        )
    resumo_do_pedido_gerado_com_a_conversa = models.CharField(
        default='',
        )
    
    def __str__(self):
        usage_id = self.id
        return f"Conversa n° {usage_id}"



