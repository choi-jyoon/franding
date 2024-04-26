from typing import Any
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView,DetailView
from cart.models import Cart, Order
from item.models import Item
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect



# Create your views here.    
    
# 장바구니 페이지
# def cart_id(request):
#     cart = Item.objects.get(pk=3)
#     cart_id = cart.user.pk
#     return cart_id


# cart_id 신경쓰지 말것
# usr_id 로 상품을 조회하자
# status로 구매여부를 확인하자
def add_cart(request,) -> Any:
    # 카트아이템에 담자
    # 카트아이템이 있는지 확인을 해야한다.
    # 카트 아이템이 아직 없다.
    # 카트아이템에 담을려면 뭐가 필요할까?
    if request.method == 'POST':

        # 유저정보: request.user, 담을 상품 : item, 수량 : click 했을 시 생김, 상태 : click을 했는데 결제를 안했을 시 False
        # item = Item.objects.all() # 상품을 가져왔다.
        user = request.user # 누가 가져왔는지 유저 정보가 필요해서 가져왔다.
        item_id = request.POST['item_id'] # 유저가 담은 상품을 가져왔다.
        item = get_object_or_404(Item, id=item_id) # Item모델에 해당 상품이 없다면 에러 발생.
        # 카트 아이템에 담았지만 아직 결제를 하지 않은 상태이다.
        status = False
        

        # 카트 아이템을 만들어야 한다. 여기까지 만들어보자.
        
        
        cart = Cart.objects.create(user=user, item=item, status=status, amount=0)
        cart.amount += 1
        cart.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) # 현재 페이지 그래로 유지


    # 만약에 추가로 담을거면 있는 카트에 담아야 한다.  
    # try:
    #     cart = Cart.objects.get(user=user, status=False)
    #     cart.amount += 1
    #     cart.save()
    # except Cart.DoesNotExist:
    #     cart = Cart(user=user, item=item, status=status, amount=amount)
    #     cart.save()
    # return redirect(request, 'cart/cart.html', {'cart': cart})

      
# 템플릿에 표시해야 함.
# 장바구니 페이지를 만들 때 새로운 함수를 만들어서 filter를 user, status 값을 가져와서 쭉 
# 뽑아주는 형태로 만들면 될 것 같다.
def cart_detail(request):
    cart = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')
    return render(request, 'cart/cart_detail.html', {'cart': cart})