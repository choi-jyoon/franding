from typing import Any
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView,DetailView
from cart.models import Cart, Order
from item.models import Item



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
    item = Item.objects.get(pk=item_id)
    try:
        cart = Order.objects.get(user=request.user, status=True)
        cart.amount += 1
        cart.save()
    except Cart.DoesNotExist:
        cart = Cart(user=request.user, item=item)
        cart.save()

    try:
        cart = Order.objects.get(user=request.user, status=True)
        cart.amount += 1
        cart.save()
    except Cart.DoesNotExist:
        cart = Cart(user=request.user, item=item)
        cart.save()
    
    return redirect(request, 'cart/cart.html', {'cart': cart})


# def cart_detail(request):
#     cart = cart_id(request)
#     return render(request, 'cart/cart.html', {'cart': cart})