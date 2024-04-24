from django.db import models
from django.contrib.auth.models import User
from item.models import Item

# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item , on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    status = models.BooleanField(default=True)
    
class Order(models.Model):
    # cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # order_cart=models.ForeignKey(OrderCart, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField(default=0)
    
class OrderCart(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

