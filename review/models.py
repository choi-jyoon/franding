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


class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
class ReviewReply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    isLike = models.BooleanField(default=False)