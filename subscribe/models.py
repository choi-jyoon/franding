from django.db import models
from django.contrib.auth.models import User
from item.models import Category1, Category2, Item

# Create your models here.

class Subscribe(models.Model):
    STATE_CHOICES = (
        (0, '신청 완료'),
        (1, '상품 선별 중'),
        (2, '상품 제공 완료'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    state = models.IntegerField(default=0, choices=STATE_CHOICES)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    
class Keyword(models.Model):
    category1 = models.ForeignKey(Category1, on_delete=models.CASCADE)
    category2 = models.ForeignKey(Category2, on_delete=models.CASCADE, null=True)
    word = models.CharField(max_length=150)
    month = models.DateField()
    
    def __str__(self):
        return self.word
    
class SubscribeKeyword(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    subscribe = models.ForeignKey(Subscribe, on_delete=models.CASCADE)