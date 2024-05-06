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


# 장바구니에 상품 추가
def add_cart(request,) -> Any:    
    if request.method == 'POST':

        # 유저정보: request.user, 담을 상품 : item, 수량 : click 했을 시 생김, 상태 : click을 했는데 결제를 안했을 시 False
        # item = Item.objects.all() # 상품을 가져왔다.
        user = request.user # 누가 가져왔는지 유저 정보가 필요해서 가져왔다.
        item_id = request.POST['item_id'] # 유저가 담은 상품을 가져왔다.
        item = get_object_or_404(Item, id=item_id) # Item모델에 해당 상품이 없다면 에러 발생.
        # 카트 아이템에 담았지만 아직 결제를 하지 않은 상태이다.
        status = False     
            
        
        cart = Cart.objects.create(user=user, item=item, status=status, amount=0)
        cart.amount += 1
        cart.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) # 현재 페이지 그래로 유지

      

# 장바구니 페이지
def cart_detail(request, total_price=0):

    # 총 가격 계산
    cart = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')

    for c in cart:        
        total_price += (c.item.price * c.amount)

    
    # 상품 추천
    product_paid_for = Cart.objects.filter(status=True).values('item_id').annotate(total_amount = Sum('amount')).order_by('-total_amount')[:3]
    best_items = []

    for item_id in product_paid_for:
        best_i = Item.objects.get(id = item_id['item_id']) # id가 item_id인 Item을 가져온다.
        best_items.append(best_i)    
    
    
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


    
    
        
    

    