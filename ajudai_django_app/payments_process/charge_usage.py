import stripe
from get_secret_variables import get_secret_var

stripe.api_key = get_secret_var("STRIPE_SECRET_KEY")

def charge_usages(total_cost, user):
    from ajudai_django_app.models import CustomUser
    
    # Retrieve customer ID from your database based on user_id
    customer_id = user.stripe_id 

    # Convert total_cost to cents (Stripe uses cents as default currency unit)
    amount = int(total_cost * 100)

    # Retrieve the default payment method for the customer
    payment_methods = stripe.PaymentMethod.list(
        customer=customer_id,
        type="card",
    )

    if not payment_methods.data:
        raise Exception("No payment method found for user")

    payment_method = payment_methods.data[0]

    # Create a PaymentIntent
    try:
        stripe.PaymentIntent.create(
            amount=amount,
            currency='brl',  # Change this to your desired currency
            customer=customer_id,
            payment_method=payment_method.id,
            confirm=True,
        )
    except stripe.error.StripeError as e:
        print(f"Charge failed: {e}")