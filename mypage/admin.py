from django.contrib import admin

from cart.models import Cart, Order, OrderCart
from .models import UserAddInfo

admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderCart)
admin.site.register(UserAddInfo)