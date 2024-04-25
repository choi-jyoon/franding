from django.db import models
from django.contrib.auth.models import User
from item.models import Item
# Create your models here.

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    star = models.IntegerField()
    content = models.TextField()