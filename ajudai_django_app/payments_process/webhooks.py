import stripe
from constants import EVENT_INVALID_PAYLOAD, EVENT_INVALID_SIGNATURE, EVENT_TYPE_TO_CHECKOUT_COMPLETE_SUCCESS, EVENT_TYPE_USAGE_PAYMENT_SUCCESS, WEBHOOK_ADESAO_ID, WEBHOOK_PAYMENT_METHOD_ID, WEBHOOK_USAGE_PAYMENT_ID
from get_secret_variables import get_secret_var

stripe.api_key = get_secret_var("STRIPE_SECRET_KEY")

#elemento para garantir que, no wbhook, apenas seja aceitas reqquisições referentes a API de pagamento em uso. No caso, da Srripe
HTTP_PAYMENT_API_SIGNATURE = 'HTTP_STRIPE_SIGNATURE'

LABEL_TO_CHECKOUT_SESSION_ID = 'id'

def get_endpoint_secret(webhook_id):
    endpoint_secret = ''

    if webhook_id == WEBHOOK_ADESAO_ID:
        endpoint_secret = get_secret_var("stripe_adesao_webhook_endpoint_secret")
    elif webhook_id == WEBHOOK_PAYMENT_METHOD_ID:
        endpoint_secret = get_secret_var("stripe_pay_method_webhook_endpoint_secret")
    elif webhook_id == WEBHOOK_USAGE_PAYMENT_ID:
        endpoint_secret = get_secret_var("stripe_usage_webhook_endpoint_secret")

    return endpoint_secret

def get_webhook_event(payload, sig_header, webhook_id):
    endpoint_secret = get_endpoint_secret(webhook_id)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        event = EVENT_INVALID_PAYLOAD
    except stripe.error.SignatureVerificationError as e:
        event =  EVENT_INVALID_SIGNATURE

    return event

def success_payment_checkout_and_section_recovery(event):
    if event['type'] == EVENT_TYPE_TO_CHECKOUT_COMPLETE_SUCCESS:
        return True
    return False

def success_payment_usage_charge(event):
    if event['type'] == EVENT_TYPE_USAGE_PAYMENT_SUCCESS:
        return True
    return False

def get_session_data(event):
    return stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )

def get_usage_payment_webhook_customer(event):
    payment_data = event['data']['object']
    customer_id = payment_data['customer']
    amount_payed = payment_data['amount']

    return customer_id, amount_payed

