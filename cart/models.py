from django.db import models
from django.contrib.auth.models import User
from item.models import Item
from payment.models import Delivery, UserCoupon
from django.db.models import Count
# Create your models here.

# CartItem
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item , on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    status = models.BooleanField(default=False) # 주문 전 = False, 주문 후 = True

    def __str__(self):
        return self.item.name
    
    def sub_total(self):
        return self.item.price * self.amount
    
    @classmethod
    def calculate_user_cart_id_count(cls, user):
        return cls.objects.filter(user=user, status=False).aggregate(id_count=Count('id'))['id_count'] or 0
    

class Order(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)  # 주문 시간
    total_price = models.IntegerField(default=0)    # 총 가격
    delivery_info =models.ForeignKey(Delivery, on_delete=models.CASCADE, null=True)  # 배송지 정보 
    user_coupon = models.ForeignKey(UserCoupon, on_delete=models.CASCADE, null=True)  # 유저 쿠폰


# 결제완료시 차례대로 delivery, order, ordercart  데이터 생성 

class OrderCart(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    is_review = models.BooleanField(default=False)  # 리뷰 작성 여부 확인 위함. 
    status = models.IntegerField(default=0) # 0: 기본 상태 1: 구매확정 2: 환불신청 3:환불완료

    def __str__(self):
        return self.cart.item.name

class Refund(models.Model):
    ordercart = models.ForeignKey(OrderCart, on_delete=models.CASCADE)
    refund_date = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField()
    status = models.BooleanField(default=True)