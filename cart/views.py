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
# from time_logger import time_logger
from my_langchain.recommend.best_item import best_items
import csv
import pandas as pd


# 상품 조회해서 csv파일로 만들기
def export_items_to_csv(filename='items.csv'):
    # Assuming 'Item' has a 'summary' and 'description' field
    items = Item.objects.all()  # Query all items from the database

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Summary', 'Description'])  # Write the header

        for item in items:
            writer.writerow([item.summary, item.description])  # Write item data


# 상품 데이터 리스트 만들기
def item_id_list(items, attributes):
    """item_id 전체 조회"""

    item_list = []
    for item in items:
        if attributes == 'id':
            item_list.append(item.id)
        elif attributes == 'name':
            item_list.append(item.name)
        elif attributes == 'summary':
            item_list.append(item.summary)
        elif attributes == 'description':
            item_list.append(item.description)

    return item_list


# 상품 데이터프레임 만들기
def item_dataFrame():
    items = Item.objects.all()  # Query all items from the database
    item_id = item_id_list(items, attributes='id')
    name = item_id_list(items, attributes='name')
    summary = item_id_list(items, attributes='summary')
    description = item_id_list(items, attributes='description')

    data = {
        'item_id': item_id,
        'name': name,
        'summary': summary,
        'description': description,
    }

    df = pd.DataFrame(data)

    return df


def item_csv_file_save():
    df = item_dataFrame()
    df.to_csv('my_langchain/csv_file/items.csv', index=False)    


# 장바구니 총량 구하기
def cart_total_price(cart, total_price=0):
    for c in cart:        
        total_price += (c.item.price * c.amount)
    
    return total_price


# 상품 추천하기
def best_cart_item(product_paid_for, attrebutes='item_id'):    
    best_items = []

    for item_id in product_paid_for:
        best_i = Item.objects.get(id = item_id[attrebutes])
        best_items.append(best_i) 

    return best_items

# admin님이 구매한 상품 리스트
# def product_paid_for_list(product_paid_for):
#     product_paid_for = Cart.objects.filter(user_id=1, status=True).values('name')
#     return product_paid_for




# 문자 읽어서 데이터베이스에 있는 상품 이름이랑 비교해서 상품 id반환 
def search_best_item():
    best_item = best_items()
    all_items = Item.objects.all()
    search_item = []
    for item in all_items:
        filter_name = item.name
        if filter_name in best_item:
            search_item.append(item)

    return search_item


# 장바구니 테이블 생성
def cart_table_create(request):
    """
    장바구니 테이블을 생성합니다.

    Returns:
        장바구니 테이블 생성 결과

    """
    item_id = request.POST['item_id']
    item = get_object_or_404(Item, id=item_id)
    cart, created = Cart.objects.get_or_create(user=request.user, item=item, status=False)
    return cart


# 체크된 상품 수량 변경
def check_item_amount(request, cart):
    cart.amount += int(request.POST['change_amount'])
    return cart


# 체크된 상품 삭제
def check_item_delete(request, checkbox_item):
    for check in checkbox_item:          
        check_item = Cart.objects.get(user=request.user, item=check, status=False) 
        check_item.delete()

    return None


# 사용자 인증 확인
def check_user_authentication(request, cart_count=None):
    """
    사용자 인증을 확인합니다.

    Returns:
        사용자 인증 결과

    """    

    # cart_count가 None이거나 길이가 0인 경우를 확인
    if cart_count is None:
        # 여기에 cart_count가 비어 있을 때 수행할 코드를 작성
        return request.user
    else:
        # cart_count에 값이 있는 경우 수행할 코드
        if request.user.is_authenticated:
            cart_count
        else:
            cart_count = 0

        return cart_count


# 장바구니 페이지
# 7.157054662704468초
# @time_logger("cart_detail")
@login_required
def cart_detail(request, best_items=search_best_item):
    """
    장바구니 페이지를 렌더링하고 체크 표시된 항목의 총 가격을 계산합니다.

    Args:
        request: HTTP 요청 객체
        total_price: 총 가격 초기값 (기본값: 0)

    Returns:
        렌더링된 장바구니 페이지

    """
    # 장바구니 필터링
    cart = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')    

    total_price = cart_total_price(cart)

    # 상품 추천 필터링
    # product_paid_for = Cart.objects.filter(status=True).values('item_id').annotate(total_amount = Sum('amount')).order_by('-total_amount')[:1]

    # best_items = best_cart_item(product_paid_for)
    
    context = {
        'user': request.user,        
        'cart': cart,
        'total_price': total_price,
        'best_items': best_items(),        
    }
    return render(request, 'cart/cart_detail.html', context)


# 장바구니 수량 변경
# 1.5220270156860352,
# 1.8930752277374268,
# 2.037010669708252,
# 1.390061616897583,
# 1.8565404415130615,초
# @time_logger("accept_ajax")
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
        cart = cart_table_create(request=request)
        
        check_item = check_item_amount(request=request, cart=cart)
        
        if check_item.amount >= 1:
            check_item.save()
        
        # 총 가격 계산
        cart_total_count = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')

        total_price = cart_total_price(cart_total_count)      
        
        context ={
            'new_amount': cart.amount,
            'total_price': total_price,
            'massage': '수량이 변경되었습니다.',
            'success': True,
        }
        return JsonResponse(context)
    


#  0.6226406097412109,
# 0.8372805118560791초
# @time_logger("cart_delete")
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

        # 체크된 상품 삭제
        check_item_delete(request=request, checkbox_item=checkbox_item)     

    return redirect('home')


# 0.5337092876434326,초
# @time_logger("badge_count")
def badge_count(request):
    cart_count = Cart.calculate_user_cart_id_count(request.user)

    # 사용자 인증 확인
    user_authentication = check_user_authentication(request, cart_count)

    context = {'cart_count': user_authentication}
    return JsonResponse(context)


class CartViewSet(viewsets.ModelViewSet):
    """
    장바구니 모델의 CRUD 작업을 수행하는 ViewSet 클래스입니다.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
        
    

    