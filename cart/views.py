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
from django.http import HttpResponse


# 장바구니 페이지
@login_required
def cart_detail(request, total_price=0):
    """
    장바구니 페이지를 렌더링하고 체크 표시된 항목의 총 가격을 계산합니다.

    Args:
        request: HTTP 요청 객체
        total_price: 총 가격 초기값 (기본값: 0)

    Returns:
        렌더링된 장바구니 페이지

    """
    cart = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')    

    for c in cart:        
        total_price += (c.item.price * c.amount)

    product_paid_for = Cart.objects.filter(status=True).values('item_id').annotate(total_amount = Sum('amount')).order_by('-total_amount')[:1]
    best_items = []

    for item_id in product_paid_for:
        best_i = Item.objects.get(id = item_id['item_id'])
        best_items.append(best_i)   
    
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
    """
    AJAX 요청을 통해 장바구니 항목의 수량을 변경하고 변경된 값을 반환합니다.

    Args:
        request: HTTP 요청 객체
        total_price: 총 가격 초기값 (기본값: 0)

    Returns:
        변경된 수량과 총 가격을 포함한 JSON 응답

    """
    if request.method == 'POST':
        item_id = request.POST['item_id']
        item = get_object_or_404(Item, id=item_id)
        cart, created = Cart.objects.get_or_create(user=request.user, item=item, status=False)
        cart.amount += int(request.POST['change_amount'])

        if cart.amount >= 1:
            cart.save()
        
        cart_total_count = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')

        for c in cart_total_count:
            total_price += (c.item.price * c.amount)       
        
        context ={
            'new_amount': cart.amount,
            'total_price': total_price,
            'massage': '수량이 변경되었습니다.',
            'success': True,
        }
        return JsonResponse(context)
    

@login_required
def cart_delete(request):
    """
    장바구니에서 선택된 항목을 삭제하고 홈 페이지로 리디렉션합니다.

    Args:
        request: HTTP 요청 객체

    Returns:
        홈 페이지로 리디렉션

    """
    if request.method == 'GET':
        checkbox_item = request.GET.getlist('item_list[]')        
                
        for check in checkbox_item:          
            check_item = Cart.objects.get(user=request.user, item=check, status=False) 
            check_item.delete()

    return redirect('home')


def badge_count(request):
    # 사용자 인증 확인
    if request.user.is_authenticated:
        cart_count = Cart.calculate_user_cart_id_count(request.user)
    else:
        cart_count = 0
    context = {'cart_count': cart_count}
    return JsonResponse(context)
    


# def badge_count(request):
#     # 사용자 인증 확인
#     if request.user.is_authenticated:
#         cart_count = Cart.calculate_user_cart_id_count(request.user)
#     else:
#         cart_count = 0

#     # 세션에 cart_count 저장
#     request.session['cart_count'] = cart_count

#     return JsonResponse({'cart_count': cart_count})


class CartViewSet(viewsets.ModelViewSet):
    """
    장바구니 모델의 CRUD 작업을 수행하는 ViewSet 클래스입니다.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
        
    

    