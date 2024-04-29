from django.db import models
from cart.models import Order
# Create your models here.

# payment
# class Order(models.Model):
    # 결제 정보 -> 카드번호, 카드 만료일, 카드 소유자, 카드 CVC, 결제 금액, 결제 상태, 결제 시간, 결제 상품
    # payment_id = models.AutoField(primary_key=True) 
    # cart_info = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # payment_time = models.DateTimeField()
    # card_number = models.CharField(max_length=16)
    # card_expire_date = models.DateField()
    # card_owner = models.CharField(max_length=30)
    # card_cvc = models.CharField(max_length=3)


# class Delivery(models.Model):
#     # 배송지 -> 받는사람, 주소, 휴대전화, 이메일, 배송 상태, 배송상품 
#     payment_info = models.ForeignKey(Order, on_delete=models.CASCADE)
#     delivery_status = models.BooleanField()
#     receiver = models.CharField(max_length=30)
#     receiver_address = models.CharField(max_length=100)
#     receiver_phone = models.CharField(max_length=11)
#     receiver_email = models.EmailField()


# class Coupon(models.Model):
#     # 쿠폰 -> 쿠폰 번호, 쿠폰 할인율, 쿠폰 사용 여부, 쿠폰 만료일
#     coupon_number = models.CharField(max_length=10)
#     coupon_discount_rate = models.IntegerField()
#     coupon_use = models.BooleanField()
#     coupon_expire_date = models.DateField()


# 쿠폰이라는 정체가 되게 애매함.
# 사람이 쿠폰을 가져옴.

# Create your models here.
class Delivery(models.Model):
    status= models.IntegerField(default=0)  # 상태: 배송 전(0), 배송 중(1) , 배송 완료(2)
    receiver = models.CharField(max_length=30)  #  받는사람
    receiver_address=models.CharField(max_length=150)   # 받는 사람 주소
    receiver_phone = models.CharField(max_length=20)    # 받는 사람 전화번호
    receiver_email = models.EmailField()    # 받는 사람 이메일
