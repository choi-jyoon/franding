from django.shortcuts import render, redirect
from cart.models import Cart, Order
from django.contrib.auth.decorators import login_required

# @login_required
def order_index(request):
    # orders = Order.objects.filter(user=request.user)
    orders = Order.objects.all()
    carts = Cart.objects.all()
    context={
        'object_list':orders
    }
    return render(request, 'mypage/order_index.html', context)