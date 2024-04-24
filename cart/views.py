from typing import Any
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView,DetailView
from cart.models import Cart, Order
from item.models import Item
from django.contrib.auth.models import User



# Create your views here.    
    
# 장바구니 페이지
# def cart_id(request):
#     cart = Item.objects.get(pk=3)
#     cart_id = cart.user.pk
#     return cart_id


# cart_id 신경쓰지 말것
# usr_id 로 상품을 조회하자
# status로 구매여부를 확인하자
def add_cart(request, item_id: Any) -> Any:
    # 카트아이템에 담자
    # 카트아이템이 있는지 확인을 해야한다.
    # 카트 아이템이 아직 없다.
    # 카트아이템에 담을려면 뭐가 필요할까?

    # 유저정보: request.user, 담을 상품 : item, 수량 : click 했을 시 생김, 상태 : click을 했는데 결제를 안했을 시 False
    item = Item.objects.get(pk=item_id) # 상품을 가져왔다.
    # 누가 가져왔는지 유저 정보가 필요하다.
    user = request.user # 유저 정보를 가져왔다.
    # 카트 아이템에 담았지만 아직 결제를 하지 않은 상태이다.
    status = False
    
    # 카트 아이템을 만들어야 한다. 여기까지 만들어보자.
    # 만약에 추가로 담을거면 있는 카트에 담아야 한다.   
    
    try:
        cart = Order.objects.get(order_id=request.user)
        cart.amount += 1
        cart.save()
    except Cart.DoesNotExist:
        cart = Cart(user=request.user, item=item)
        cart.save()

    # try:
    #     cart = Order.objects.get(user=request.user, status=True)
    #     cart.amount += 1
    #     cart.save()
    # except Cart.DoesNotExist:
    #     cart = Cart(user=request.user, item=item)
    #     cart.save()
    
    return redirect(request, 'cart/cart.html', {'cart': cart})


# def cart_detail(request):
#     cart = cart_id(request)
#     return render(request, 'cart/cart.html', {'cart': cart})