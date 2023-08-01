from django.contrib import admin
from django.db.models import Count

from constants import STANDART_PERIOD
from .models import ChatBot, Conversa, CustomUser, DadosClienteCadatrado, PaymentsForUseMadde, Pedido, Product, Adesao_Purchase, Premium_User_Payment_Method_Registration

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_total_conversas', 'get_product_name', 'get_conversas_a_pagar') 

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(total_conversas=Count('chatbot__conversa', distinct=True))
        return queryset

    def get_product_name(self, obj):
        if obj.userIsPremium() == False:
            return "Usuario Free"
        else:
            product, _, _ = obj.current_user_plan_price_and_conversas_a_pagar(STANDART_PERIOD)
            return product.name if product else "None"
            
    get_product_name.short_description = 'Plano Atual'

    def get_conversas_a_pagar(self, obj):
        if obj.userIsPremium() == False:
            return 0
        else:
            _, _, conversas_a_pagar = obj.current_user_plan_price_and_conversas_a_pagar(STANDART_PERIOD)
            return conversas_a_pagar
            
    get_conversas_a_pagar.short_description = 'Conversas No Periodo Atual'


    def get_total_conversas(self, obj):
        return obj.total_conversas
    get_total_conversas.short_description = 'Total Conversas'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product)
admin.site.register(ChatBot)
admin.site.register(Conversa)
admin.site.register(Pedido)
admin.site.register(Adesao_Purchase)
admin.site.register(Premium_User_Payment_Method_Registration)
admin.site.register(DadosClienteCadatrado)
admin.site.register(PaymentsForUseMadde)
