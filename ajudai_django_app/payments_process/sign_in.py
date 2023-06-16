import stripe
from get_secret_variables import get_secret_var

stripe.api_key = get_secret_var("STRIPE_SECRET_KEY")

def return_setup_future_payments_checkout_session(success_ur, cancel_url, user):
    from ajudai_django_app.models import CustomUser

    customer_id = user.stripe_id


    checkout_session = stripe.checkout.Session.create(
            customer=customer_id, 
            payment_method_types=['card'],
            mode='setup',
            success_url=success_ur,
            cancel_url=cancel_url,
            )

    return checkout_session

def return_adesao_checkout_session(priceID, success_ur, cancel_url):
    checkout_session = stripe.checkout.Session.create(
                line_items=[{
                    'price' : priceID,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_ur,
                cancel_url=cancel_url,
            )

    return checkout_session

def create_stripe_customer(user):
    from ajudai_django_app.models import CustomUser

    customer = stripe.Customer.create(
        description=f"Customer for user_id {user.id}",
        email=user.email,  # It's a good practice to associate Stripe Customer with user's email
    )
    user.stripe_id = customer.id
    user.save()


def return_checkout_session_url(checkout_session):
    return checkout_session.url

def return_checkout_session_id(checkout_session):
    return checkout_session.id