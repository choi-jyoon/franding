from django.db import models
from django.contrib.auth.models import User
from item.models import Item
from cart.models import OrderCart
from django.utils import timezone
# Create your models here.

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    orderCart = models.ForeignKey(OrderCart, on_delete=models.CASCADE, default=1)
    star = models.IntegerField()
    content = models.TextField()
    datetime = models.DateTimeField(default=timezone.now)
