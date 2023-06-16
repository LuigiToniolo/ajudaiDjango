#MAIN APP AND COMPANY DEFFINITIONS

MAIN_APP_NAME = 'ajudai_django_app'
SUPPORT_EMAIL = ''
FANTASY_NAME = 'Ajudaí'

DOMAIN = 'http://127.0.0.1:8000' #TODO PREENCHER COM URL REAL EM PRODUÇÃO (do projeto python no pythonanywhere, que deve ser um um sub da landing page)

#--------------------------------------------------------------------
#USUARIOS/PAGAMENTOS/PRUDUTOS
USER_LEVEL_FREE = 'free_user'
USER_LEVEL_PREMIUM = 'premium_user'

DIAS_TOLERACIA_INADIMPLECIA = 7

PRUDUCT_TYPE_PLAN = 'plan'
PRUDUCT_TYPE_ADESAO = 'adesao'
PRUDUCT_TYPE_CONVERSA_AVULSA = 'conversa_avulsa'

PAYMENT_METHOD_REGISTRATION_STATUS_PENDING = 'payment_method_pending'
PAYMENT_METHOD_REGISTRATION_STATUS_SUCCESS = 'payment_method_success'
PAYMENT_METHOD_REGISTRATION_STATUS_FAILING = 'payment_method_failing'

USAGE_PAYED_STATUS_PENDING = 'pending_payment'
USAGE_PAYED_STATUS_SUCCESS = 'payment_success'

ADESAO_PURCHASE_STATUS_PENDING = 'Pending'
ADESAO_PURCHASE_STATUS_PROCESSED = 'Processed'
ADESAO_PURCHASE_STATUS_CALCELED = 'Canceled'

EVENT_INVALID_PAYLOAD = 'invalid payload'
EVENT_INVALID_SIGNATURE = 'invalid sgnature'
EVENT_TYPE_TO_CHECKOUT_COMPLETE_SUCCESS = 'checkout.session.completed'
EVENT_TYPE_USAGE_PAYMENT_SUCCESS = 'payment_intent.succeeded'

USER_PAYMENT_METHOD_NOT_REGISTERED = 'payment_method_not_registered'
USER_PAYMENT_METHOD_STATUS_OK = 'payment_method_registered_ok'
USER_PAYMENT_METHOD_FAILED = 'payment_method_failed'

PAYMENT_PERIOD_DAILY = 'daily'
PAYMENT_PERIOD_MONTHLY = 'monthly'
PAYMENT_PERIOD_ANUALY = 'anualy'
STANDART_PERIOD = PAYMENT_PERIOD_MONTHLY

CONVERSA_PAGA = 'paga'
CONVERSA_PAGAMENTO_PENDENTE = 'pendente'
CONVERSA_AGUARDANDO_VENCIMENTO = 'aguardando_vencimento'

WEBHOOK_ADESAO_ID = 'webhook_adesao'
WEBHOOK_PAYMENT_METHOD_ID = 'webhook_method'
WEBHOOK_USAGE_PAYMENT_ID = 'webhook_usage_payment'

#---------------------------------------------------------------------
#API RELATED
AI_PROVIDER_OPEN_AI = "open_ai"

GPT3_MODEL_NAME = 'gpt-3.5-turbo'

GPT3_TOKEK_LIMIT = 4096

MAX_INSTRUCTIONS_RATE_SIZE = 0.95
#o limite deixado para a pergunta/prompt é, então 0,05 menos o limite de reserva para a resposta abaixo


MAX_PROMPT_IN_CHARS = int(GPT3_TOKEK_LIMIT * 4)
MAX_CHAR_INSTRUCTIONS_CHATBOT_FORM = int(GPT3_TOKEK_LIMIT *MAX_INSTRUCTIONS_RATE_SIZE * 4)

AWNSER_WHEN_MESSAGE_IS_OVER_THE_LIMIT = "A sua mensagem está muito grande para ser processada. Por favor, tente falar em menos palavras ou dividir a sua pergunta em mensagens diferentes."

#the gpt chat model does not need to leave space for the awnser
MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER = 0.0

CHAT_API_GENERAL_ERROR_MESSAGE = 'Me descuple, tive problemas para conseguir obter uma resposta para você. Por favor, tente novamente mais tarde...'
CHAT_API_MESSAGE_AND_AWNSER_OVERLIMT_EVEN_TRYING_TO_SHORT = 'Desulpe, a resposta que você que quer ocuparia um espaço de maior do que sou capaz de processar. Por favor, pergunte algo mais específico.'

TOKEN_LIMIT_MARGIN = 0.08
#---------------------------------------------------------------------
#FORM FIELD LIMITS AND SIZES
REGISTER_FIELD_STANDART_SIZE_IN_PX=300
REGISTER_EMAIL_FIELD_SIZE_IN_PX=400
FULL_NAME_FIELD_SIZE_IN_PX = 400
CELLPHONE_FIELD_SIZE_IN_PX = 200
COMPANY_NAME_FIELD_SIZE_IN_PX = 400
WHATS_APP_TOKEN_FILD_SIZE_IN_PX = 700
FACEBOOK_PAG_ID_FIELD_SIZE_IN_PX = 300
CHATBOT_NAME_FIELD_SIZE_IN_PX = 300

ADITIONAL_INTRUCTIONS_FIELD_SIZE_IN_PX = 900
ADITIONAL_INTRUCTIONS_FIELD_ROWS = 5

#---------------------------------------------------------------------
#FORM IDS AND NAMES AND VALUES
USER_NAME_FIELD_ID = 'username'
PASSWORD_FIELD_ID = 'password'

BRL_CURRENCY_SIMBOL = 'BRL'

ADITIONAL_INTRUCTIONS_FIELD_ID = 'aditional-instructions-textarea'
ADITIONAL_INTRUCTIONS_FIELD_NAME = 'aditional_intructions'

#---------------------------------------------------------------------
# MODELS
STATUS_CONVERSA_EM_ANDAMENTO = 'conversa_em_andamento'
STATUS_CONVERSA_PEDIDO_REALIZADO = 'conversa_pedido_realizado'
STATUS_CONVERSA_FALHA = 'conversa_falhou'

STATUS_PEDIDO_PENDENTE_DE_ENTREGA = 'pendente_de_entrega'
STATUS_PEDIDO_ENTREGUE = 'entregue'
STATUS_PEDIDO_CANCELADO = 'cancelado'

#---------------------------------------------------------------------
#TEXTS