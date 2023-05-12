#MAIN APP AND COMPANY DEFFINITIONS

MAIN_APP_NAME = 'ajudai_django_app'
SUPPORT_EMAIL = ''
FANTASY_NAME = 'Ajudaí'


#---------------------------------------------------------------------
#API RELATED
AI_PROVIDER_OPEN_AI = "open_ai"

GPT3_MODEL_NAME = 'gpt-3.5-turbo'

GPT3_TOKEK_LIMIT = 4096

MAX_INSTRUCTIONS_RATE_SIZE = 0.95
#o limite deixado para a pergunta/prompt é, então 0,05 menos o limite de reserva para a resposta abaixo


MAX_PROMPT_IN_CHARS = int(GPT3_TOKEK_LIMIT * 4)
MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM = int(GPT3_TOKEK_LIMIT *MAX_INSTRUCTIONS_RATE_SIZE * 4)

#---------------------------------------------------------------------
#FORM FIELD LIMITS AND SIZES
REGISTER_FIELD_STANDART_SIZE_IN_PX=300
REGISTER_EMAIL_FIELD_SIZE_IN_PX=400
FULL_NAME_FIELD_SIZE_IN_PX = 400
CELLPHONE_FIELD_SIZE_IN_PX = 200
COMPANY_NAME_FIELD_SIZE_IN_PX = 400

#---------------------------------------------------------------------
#FORM IDS AND NAMES AND VALUES
USER_NAME_FIELD_ID = 'username'
PASSWORD_FIELD_ID = 'password'

BRL_CURRENCY_SIMBOL = 'BRL'

#---------------------------------------------------------------------
#TEXTS