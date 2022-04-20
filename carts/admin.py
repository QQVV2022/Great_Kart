from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_add')


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart','user' , 'product',  'quantity',  'is_available')

admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Cart, CartAdmin)