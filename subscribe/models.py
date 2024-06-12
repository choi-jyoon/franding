from django.db import models
from django.contrib.auth.models import User
from item.models import Category1, Category2, Item
from payment.models import Delivery

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
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, null=True)
    
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
    
class SubscribePayInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    aid = models.CharField(max_length=50, null = True)
    tid = models.CharField(max_length=50)
    cid = models.CharField(max_length=50)
    sid = models.CharField(max_length=30,null=True) 
    partner_order_id = models.CharField(max_length=150, null=True)
    partner_user_id = models.CharField(max_length=150, null=True)
    payment_method_type = models.CharField(max_length=30)
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    total_amount = models.IntegerField()
    status = models.CharField(max_length=20, default='prepared')  # 결제 상태 (예: prepared, completed, cancelled)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(auto_now_add=True)
    next_payment_date = models.DateTimeField(null=True)  # 다음 결제 날짜
    payment_interval = models.IntegerField(default=30)  # 결제 주기 (일 단위)
    last_payment_date = models.DateTimeField(null=True, blank=True)  # 마지막 결제일 추가