from django.db import models
from django.contrib.auth.models import User
from item.models import Item

# Create your models here.

# CartItem
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item , on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.item.name
    

# 나에겐 필요가 없다.
# Cart
class Order(models.Model):
    # cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # order_cart=models.ForeignKey(OrderCart, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField(default=0)

    def __str__(self):
        return self.pk


# 나에겐 필요가 없다.
class OrderCart(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    is_review = models.BooleanField(default=False)  # 리뷰 작성 여부 확인 위함. 

""" cart = 1, cart = 2 cart = 3
cartitem 
cart1 명훈 item3 status = True
cart2 명훈 자동차 
cart3 명훈 컴퓨터
cart4 명훈 노트북
cart5 명훈 자동차
누가 뭐를 
명훈이라는 id로 조회할 수 있다.


user 1 조회를 해서 user1이 산 상품을 조회를 하겠다"""