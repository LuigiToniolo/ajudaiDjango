from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
import json

from ajudai_django_app.models import ChatBot, CustomUser
from constants import ADITIONAL_INTRUCTIONS_FIELD_ID, ADITIONAL_INTRUCTIONS_FIELD_NAME, ADITIONAL_INTRUCTIONS_FIELD_ROWS, ADITIONAL_INTRUCTIONS_FIELD_SIZE_IN_PX, CELLPHONE_FIELD_SIZE_IN_PX, CHATBOT_NAME_FIELD_SIZE_IN_PX, COMPANY_NAME_FIELD_SIZE_IN_PX, FACEBOOK_PAG_ID_FIELD_SIZE_IN_PX, FULL_NAME_FIELD_SIZE_IN_PX, MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, PASSWORD_FIELD_ID, REGISTER_EMAIL_FIELD_SIZE_IN_PX, REGISTER_FIELD_STANDART_SIZE_IN_PX, USER_NAME_FIELD_ID, WHATS_APP_TOKEN_FILD_SIZE_IN_PX

class JSONInput(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        if value:
            value = json.dumps(value, indent=2)
        return super().render(name, value, attrs, renderer)
    
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
                # 'style': 
                # 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)
                }
            )
        )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                'name': PASSWORD_FIELD_ID, 
                'id': PASSWORD_FIELD_ID, 
                # 'style': 'width: {}px;'.format(REGISTER_FIELD_STANDART_SIZE_IN_PX)
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
        required=False,
        max_length=MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM, 
        label='Cardápio de restaurante (com nomes dos pratos, ingredientes e preços) (caso o cardápio esteja registrado na própria API, deixar em branco)',
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
        required=False,
        label='Descrição função com informações do cardápio (caso o cardápio esteja registrado na própria API, deixar em branco)',
        initial='Obtém uma informação específica, ou um conjunto de informações específicas contidas no cardápio, como nome do produto, tamanho, ingredientes e preço',
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

    chatbot_has_products_catalog = forms.BooleanField(
        label='Você possui um cardápio (catálogo de produtos) registrado na API?',
        required=False,
    )

    initial_message_text = forms.CharField(
        label='Mensagem inicial de envio de cardápio',
        required=False,
        widget=forms.TextInput(attrs={
            # 'style': 'width: {}px;'.format(WHATS_APP_TOKEN_FILD_SIZE_IN_PX)
            })
    )

    catalog_id = forms.CharField(
        required=False,
        label='ID do catálogo (conforme adicionado no WABA)',
        widget=forms.TextInput(attrs={
            # any additional attributes you want
        })
    )

    sections_and_products = forms.CharField(
        required=False,
        label='Lista de IDs e Nomes de Produtos (conforme adicionado no WABA)',
        widget=JSONInput(attrs={'cols': 80, 'rows': 20}),
        initial=json.dumps({
            "product_items": [
                {
                    "product_retailer_id" : "",
                    "nome_do_produto" : "",
                    "preco" : 0.00,
                }
            ]
        }, indent=2)
    )

    class Meta:
        model = ChatBot
        fields = [
            'nome_do_chatbot', 'whatsapp_number', 'whats_app_api_auth_token', 'facebook_page_id', ADITIONAL_INTRUCTIONS_FIELD_NAME, 'cardapio', 'descricao_funcao_cardapio', 'chatbot_has_products_catalog', 'initial_message_text', 'catalog_id', 'sections_and_products']

    def clean_sections_and_products(self):
        data = self.cleaned_data['sections_and_products']
        try:
            parsed_data = json.loads(data)
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON format")

        return parsed_data
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
    conversa_id = forms.IntegerField()

class ConversationLimitForm(forms.Form):
    conversation_limit = forms.IntegerField(min_value=0, max_value=20000)
    limit_on = forms.BooleanField(required=False)

class LigarDesligarTodosChatbotsForm(forms.Form):
    chatbots_on = forms.BooleanField(required=False)