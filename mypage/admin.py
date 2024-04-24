from django.contrib import admin

from cart.models import Cart, Order, OrderCart

admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderCart)