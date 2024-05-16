from typing import Any
from django.shortcuts import render, redirect
from cart.models import Cart
from item.models import Item
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
import json
from rest_framework import viewsets
from .serializers import CartSerializer


# Create your views here.    


# 장바구니 페이지
@login_required
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
    
    
    # context에 담아 보내기
    context = {
        'user': request.user,        
        'cart': cart,
        'total_price': total_price,
        'best_items': best_items,        
    }
    return render(request, 'cart/cart_detail.html', context)


# 장바구니 수량 변경
@login_required
def accept_ajax(request, total_price=0):
    if request.method == 'POST':
        item_id = request.POST['item_id'] # 새로운 카트 수량을 1개 업데이트
        # new_amount = request.POST['new_amount']
        item = get_object_or_404(Item, id=item_id)
        cart, created = Cart.objects.get_or_create(user=request.user, item=item, status=False)
        cart.amount += int(request.POST['change_amount'])

        # 수량이 1개 이상일 때만 저장
        if cart.amount >= 1:
            cart.save()
        
        
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
    

@login_required
def cart_delete(request):
    if request.method == 'GET':
        checkbox_item = request.GET.getlist('item_list[]')        
                

        for check in checkbox_item:          

            check_item = Cart.objects.get(user=request.user, item=check, status=False) 
            check_item.delete()

    # return redirect('cart:cart_detail')
    return redirect('home')


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer   
    
        
    

    