from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm

from ajudai_django_app.models import CustomUser
from constants import CELLPHONE_FIELD_SIZE_IN_PX, COMPANY_NAME_FIELD_SIZE_IN_PX, FULL_NAME_FIELD_SIZE_IN_PX, PASSWORD_FIELD_ID, REGISTER_EMAIL_FIELD_SIZE_IN_PX, REGISTER_FIELD_STANDART_SIZE_IN_PX, USER_NAME_FIELD_ID

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label='Email corporativo',
        widget=forms.TextInput(attrs={'style': 'width: {}px;'.format(REGISTER_EMAIL_FIELD_SIZE_IN_PX)})
        )
    username = forms.CharField(
        label='Nome de usuário',
        widget=forms.TextInput(attrs={'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)})
        )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)})
        )
    password2 = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)})
        )
    full_name = forms.CharField(
        label='Nome completo',
        widget=forms.TextInput(attrs={'style': 'width: {}px;'.format(FULL_NAME_FIELD_SIZE_IN_PX)})
    )
    cell_phone = forms.CharField(
        label='Celular',
        widget=forms.TextInput(attrs={'style': 'width: {}px;'.format(CELLPHONE_FIELD_SIZE_IN_PX)})
    )
    company_name = forms.CharField(
        label='Nome da empresa',
        widget=forms.TextInput(attrs={'style': 'width: {}px;'.format(COMPANY_NAME_FIELD_SIZE_IN_PX)})
    )
    segmento = forms.CharField(
        label='Segmento',
        widget=forms.TextInput(attrs={'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)})
    )
    cargo_atual = forms.CharField(
        label='Cargo atual',
        widget=forms.TextInput(attrs={'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'full_name', 'email', 'cell_phone', 'company_name', 'segmento', 'cargo_atual', 'password1', 'password2')

    def clean_email(self, repeatedEmailErrorMessage = 'This email is already registered!'):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(repeatedEmailErrorMessage)
        return email

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nome de Usuário",
        widget=forms.TextInput(
            attrs={
                'name': USER_NAME_FIELD_ID, 
                'id': USER_NAME_FIELD_ID, 
                'style': 
                'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)
                }
            )
        )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                'name': PASSWORD_FIELD_ID, 
                'id': PASSWORD_FIELD_ID, 
                'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)
                }
            )
        )
    
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Senha atual")
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Nova senha")
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirme a nova senha")