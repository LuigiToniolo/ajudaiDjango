from django.contrib import admin
from ajudai_django_app.models import ChatBot, Conversa, CustomUser, Pedido, Product

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(ChatBot)
admin.site.register(Conversa)
admin.site.register(Pedido)
