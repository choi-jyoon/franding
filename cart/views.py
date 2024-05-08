from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView,DetailView
from cart.models import Cart, Order
from item.models import Item
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum


# Create your views here.    
    
# 장바구니 페이지
# def cart_id(request):
#     cart = Item.objects.get(pk=3)
#     cart_id = cart.user.pk
#     return cart_id



# 장바구니 페이지
def cart_detail(request, total_price=0):

    # 총 가격 계산
    cart = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')

    for c in cart:        
        total_price += (c.item.price * c.amount)

    
    # 상품 추천

    # 1. 가장 많이 팔린 상품
    product_paid_for = Cart.objects.filter(status=True).values('item_id').annotate(total_amount = Sum('amount')).order_by('-total_amount')[:1]
    best_items = []

    for item_id in product_paid_for:
        best_i = Item.objects.get(id = item_id['item_id']) # id가 item_id인 Item을 가져온다.
        best_items.append(best_i)


    #    
    
    
    context = {
        'cart': cart,
        'total_price': total_price,
        'best_items': best_items,
        
    }
    return render(request, 'cart/cart_detail.html', context)


# 장바구니 수량 변경
def accept_ajax(request, total_price=0):
    if request.method == 'POST':
        item_id = request.POST['item_id'] # 새로운 카트 수량을 1개 업데이트
        # new_amount = request.POST['new_amount']
        item = get_object_or_404(Item, id=item_id)
        cart, created = Cart.objects.get_or_create(user=request.user, item=item, status=False)
        cart.amount += int(request.POST['amountChange'])

        # 수량이 1개 이상일 때만 저장
        if cart.amount >= 1:
            cart.save()
        elif cart.amount == 0:
            cart.amount += 1
        
        
        cart_total_count = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')

        for c in cart_total_count:
            total_price += (c.item.price * c.amount)       
        

        # 변경된 값을 반환
        context ={
            'new_amount': cart.amount,
            'total_price': total_price,
            'massage': '수량이 변경되었습니다.',
            'success': True,
        }
        return JsonResponse(context)


    
    
        
    

    