from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Delivery(models.Model):
    status= models.IntegerField(default=0)  # 상태: 배송 전(0), 배송 중(1) , 배송 완료(2)
    receiver = models.CharField(max_length=30)  #  받는사람
    # receiver_address=models.CharField(max_length=150)   
    receiver_postcode = models.CharField(max_length=6, null=True)   # 받는 사람 주소(우편번호)
    receiver_address = models.TextField(null=True)
    receiver_detailAddress = models.CharField(max_length=100, null=True)
    receiver_extraAddress = models.CharField(max_length=100, null=True)
    receiver_phone = models.CharField(max_length=20)    # 받는 사람 전화번호
    receiver_email = models.EmailField(null=True)    # 받는 사람 이메일


class Coupon(models.Model):
    name = models.CharField(max_length=100)
    discount_rate = models.IntegerField()
    date_of_use = models.IntegerField(default=30)
    
class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    