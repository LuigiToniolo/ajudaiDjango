from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm

from ajudai_django_app.models import ChatBot, CustomUser
from constants import ADITIONAL_INTRUCTIONS_FIELD_ID, ADITIONAL_INTRUCTIONS_FIELD_NAME, ADITIONAL_INTRUCTIONS_FIELD_ROWS, ADITIONAL_INTRUCTIONS_FIELD_SIZE_IN_PX, CELLPHONE_FIELD_SIZE_IN_PX, CHATBOT_NAME_FIELD_SIZE_IN_PX, COMPANY_NAME_FIELD_SIZE_IN_PX, FACEBOOK_PAG_ID_FIELD_SIZE_IN_PX, FULL_NAME_FIELD_SIZE_IN_PX, MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, PASSWORD_FIELD_ID, REGISTER_EMAIL_FIELD_SIZE_IN_PX, REGISTER_FIELD_STANDART_SIZE_IN_PX, USER_NAME_FIELD_ID, WHATS_APP_TOKEN_FILD_SIZE_IN_PX

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label='Email corporativo',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(REGISTER_EMAIL_FIELD_SIZE_IN_PX)
            })
        )
    username = forms.CharField(
        label='Nome de usuário',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)
            })
        )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            # 'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)
            })
        )
    password2 = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={
            # 'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)
            })
        )
    full_name = forms.CharField(
        label='Nome completo',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(FULL_NAME_FIELD_SIZE_IN_PX)
            })
    )
    cell_phone = forms.CharField(
        label='Celular',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(CELLPHONE_FIELD_SIZE_IN_PX)
            })
    )
    company_name = forms.CharField(
        label='Nome da empresa',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(COMPANY_NAME_FIELD_SIZE_IN_PX)
            })
    )
    segmento = forms.CharField(
        label='Segmento',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)
            })
    )
    cargo_atual = forms.CharField(
        label='Cargo atual',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)
            })
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

class ChatBotForm(forms.ModelForm):
    nome_do_chatbot = forms.CharField(
        label='De um nome de identificação para o chatbot',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(CHATBOT_NAME_FIELD_SIZE_IN_PX)
            })
    )
    aditional_intructions = forms.CharField(
        max_length=MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, 
        label='Instruções para o Chatbot',
        widget=forms.Textarea(
            attrs={
                # 'style': 'width: {}px;'.format(ADITIONAL_INTRUCTIONS_FIELD_SIZE_IN_PX),
                'rows': ADITIONAL_INTRUCTIONS_FIELD_ROWS ,
                'id' : ADITIONAL_INTRUCTIONS_FIELD_ID,
                'data-max-height': '350',
                }
            )
        )
    cardapio = forms.CharField(
        max_length=MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, 
        label='Cardápio de restaurante (com nomes dos pratos, ingredientes e preços)',
        widget=forms.Textarea(
            attrs={
                # 'style': 'width: {}px;'.format(ADITIONAL_INTRUCTIONS_FIELD_SIZE_IN_PX),
                'rows': ADITIONAL_INTRUCTIONS_FIELD_ROWS ,
                'id' : ADITIONAL_INTRUCTIONS_FIELD_ID,
                'data-max-height': '350',
                }
            )
        )
    descricao_funcao_cardapio = forms.CharField(
        label='Descrição função com informações do cardápio',
        initial='Obtém uma informação específica, ou um conjunto de informações específicas contidas no cardápio, como nome do produto, tamanho, ingredientes e preço',
        )
    descricao_informacao_solicitada_do_cardapio = forms.CharField(
        label='Descrição do formato da informação a ser solicitada do cardápio',
        initial='A informação a ser obtida através do cardápio, por exemplo, ingredientes da pizza de mussarela, preço do refrigerante coca cola lata, preço da pizza de alho'
        )
    whatsapp_number = forms.CharField(
        label='Número WhatsApp Business',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(CELLPHONE_FIELD_SIZE_IN_PX)
            })
    )
    whats_app_api_auth_token = forms.CharField(
        label='Token de Autenticação API do Whatsapp (conforme instruções)',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(WHATS_APP_TOKEN_FILD_SIZE_IN_PX)
            })
    )
    facebook_page_id = forms.CharField(
        label='Page ID do Facebook (conforme instruções)',
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(FACEBOOK_PAG_ID_FIELD_SIZE_IN_PX)
            })
    )
    
    class Meta:
        model = ChatBot
        fields = ['nome_do_chatbot', 'whatsapp_number', 'whats_app_api_auth_token', 'facebook_page_id', ADITIONAL_INTRUCTIONS_FIELD_NAME, 'cardapio', 'descricao_funcao_cardapio', 'descricao_informacao_solicitada_do_cardapio']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
    conversa_id = forms.IntegerField()

class ConversationLimitForm(forms.Form):
    conversation_limit = forms.IntegerField(min_value=0, max_value=20000)
    limit_on = forms.BooleanField(required=False)