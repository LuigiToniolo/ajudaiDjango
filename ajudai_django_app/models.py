from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import Group, Permission
from django.core.validators import RegexValidator

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


