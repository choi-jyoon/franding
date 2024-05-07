from django.db import models
from django.contrib.auth.models import User
from item.models import Category1

# Create your models here.

class Subscribe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    
class Keyword(models.Model):
    category1 = models.ForeignKey(Category1, on_delete=models.CASCADE)
    word = models.CharField(max_length=150)
    month = models.DateField()
    
    def __str__(self):
        return self.word
    
class SubscribeKeyword(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    subscribe = models.ForeignKey(Subscribe, on_delete=models.CASCADE)