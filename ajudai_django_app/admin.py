from django.contrib import admin
from ajudai_django_app.models import ChatBot, Conversa, CustomUser, DadosClienteCadatrado, PaymentsForUseMadde, Pedido, Product, Adesao_Purchase, Premium_User_Payment_Method_Registration

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(ChatBot)
admin.site.register(Conversa)
admin.site.register(Pedido)
admin.site.register(Adesao_Purchase)
admin.site.register(Premium_User_Payment_Method_Registration)
admin.site.register(DadosClienteCadatrado)
admin.site.register(PaymentsForUseMadde)
