from django.db import models


# Create your models here.

# class Coupon(models.Model):
#     # 쿠폰 -> 쿠폰 번호, 쿠폰 할인율, 쿠폰 사용 여부, 쿠폰 만료일
#     coupon_number = models.CharField(max_length=10)
#     coupon_discount_rate = models.IntegerField()
#     coupon_use = models.BooleanField()
#     coupon_expire_date = models.DateField()



# Create your models here.
class Delivery(models.Model):
    status= models.IntegerField(default=0)  # 상태: 배송 전(0), 배송 중(1) , 배송 완료(2)
    receiver = models.CharField(max_length=30)  #  받는사람
    receiver_address=models.CharField(max_length=150)   # 받는 사람 주소
    receiver_phone = models.CharField(max_length=20)    # 받는 사람 전화번호
    receiver_email = models.EmailField()    # 받는 사람 이메일


    
