from django.shortcuts import render, redirect
from cart.models import Cart, Order, OrderCart
from .models import UserAddInfo
from django.contrib.auth.decorators import login_required

@login_required
def order_index(request):
    user_order_carts = OrderCart.objects.filter(cart__user=request.user)
    context={
        'object_list':user_order_carts
    }
    return render(request, 'mypage/order_index.html', context)

@login_required
def user_info(request):
    user_info = UserAddInfo.objects.get(user=request.user)
    context={
        'object':user_info
    }
    return render(request, 'mypage/user_info.html', context)