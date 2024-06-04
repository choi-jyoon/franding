from django.shortcuts import render, redirect
from cart.models import Cart, Order, OrderCart
from mypage.models import UserAddInfo
from .models import Delivery
import requests
import os
from dotenv import load_dotenv
from django.contrib import messages
from django.http import HttpResponseRedirect

load_dotenv()
admin_key = os.getenv('admin_key')

def payment_list(request, total_price=0):
    current_domain = request.get_host()
    template_name = 'payment/payment_info.html'
    user=request.user
    cnt = 0
    total_amount = 0
    check_item_list = []

    

    if request.method == 'GET': # True
        if 'checkbox' not in request.GET:
            messages.warning(request, '상품을 1개 이상 주문하셔야 합니다.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            checkbox_item = request.GET.getlist('checkbox') 
            request.session['checkbox_item'] = checkbox_item
    
        
    checkbox_item = request.session.get('checkbox_item')
                
    try:
        userinfo = UserAddInfo.objects.get(user=request.user) # 유저정보가 있다면 가져오기
    except UserAddInfo.DoesNotExist:
        userinfo = None
    

    for check in checkbox_item:   
        try:
            # 만약 check가 숫자가 아니라면 ValueError가 발생
            check = int(check)   
        except ValueError: 
            print('선택된 상품이 없습니다.') 
            
        check_item = Cart.objects.get(user=request.user, item=check, status=False) 
        check_item_list.append(check_item)
        total_price += (check_item.item.price * check_item.amount)
        # 배송비
        if total_price < 50000:
            shipping_fee = 3000
            total_price += shipping_fee
        else:
            shipping_fee = 0
        # 잠깐 주석처리
        cnt += 1
        # total_price += (check_item.item.price * check_item.amount)  # 총 가격
        total_amount += check_item.amount  # 총 수량
        item_name = check_item.item.name # 대표 구매 물품 이름
    if cnt > 1:
        item_name += '외 {}건'.format(cnt-1)     
                          
           
    if request.method == "POST": # False
        # 배송정보를 session에 저장
        request.session['delivery_info'] = {
            'receiver': request.POST.get('receiver'),
            'receiver_postcode': request.POST.get('receiver_postcode'),
            'receiver_address': request.POST.get('receiver_address'),
            'receiver_detailAddress': request.POST.get('receiver_detailAddress'),
            'receiver_extraAddress': request.POST.get('receiver_extraAddress'),
            'receiver_phone': request.POST.get('receiver_phone'),
            'receiver_email': request.POST.get('receiver_email')
        }
        request.session['total_price'] = total_price
        
        URL = 'https://kapi.kakao.com/v1/payment/ready'
        headers = {
            "Authorization": "KakaoAK " + admin_key,   # 변경불가
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",  # 변경불가
        }
        data = {
            "cid": "TC0ONETIME",    # 테스트용 코드
            "partner_order_id": "100",     # 주문번호
            "partner_user_id": "{}".format(user),    # 유저 아이디    # 유저 아이디
            "item_name": "{}".format(item_name),        # 구매 물품 이름
            "quantity": "{}".format(total_amount),                # 구매 물품 수량
            "total_amount": "{}".format(total_price),        # 구매 물품 가격
            "tax_free_amount": "0",         # 구매 물품 비과세
            'approval_url':f'http://{current_domain}/payment/paysuccess', 
            'fail_url':f'http://{current_domain}/payment/payfail',
            'cancel_url':f'http://{current_domain}/payment/paycancel'
        }

        res = requests.post(URL, data=data, headers=headers)
        request.session['tid'] = res.json()['tid']      # 결제 승인시 사용할 tid를 세션에 저장
        next_url = res.json()['next_redirect_pc_url']   # 결제 페이지로 넘어갈 url을 저장
        return redirect(next_url)
    
    context = {
            'item_list': check_item_list,
            'total_price': total_price,
            'shipping_fee' : shipping_fee,
            'userinfo' : userinfo
    }
    
    return render(request, template_name, context)
        

def paysuccess(request):
    user=request.user
    cart_list = []
    deliveryinfo_session = request.session.get('delivery_info')
    total_price = request.session.get('total_price')
    
    if not deliveryinfo_session or not total_price:
        return redirect('mypage:order_index')
    
    checkbox_item = request.session.get('checkbox_item')
    
    for check in checkbox_item:   
        try:
            # 만약 check가 숫자가 아니라면 ValueError가 발생
            check = int(check)   
        except ValueError: 
            print('선택된 상품이 없습니다.') 
            
        check_item = Cart.objects.get(user=request.user, item=check, status=False) 
        cart_list.append(check_item)
    
    
    # 배송 정보 생성
    delivery_info = Delivery.objects.create(
        receiver=deliveryinfo_session['receiver'],
        receiver_postcode=deliveryinfo_session['receiver_postcode'],
        receiver_address=deliveryinfo_session['receiver_address'],
        receiver_detailAddress=deliveryinfo_session['receiver_detailAddress'],
        receiver_extraAddress=deliveryinfo_session['receiver_extraAddress'],
        receiver_phone=deliveryinfo_session['receiver_phone'],
        receiver_email=deliveryinfo_session['receiver_email']
    )

    # 주문 생성
    order = Order.objects.create(
        total_price=total_price,
        delivery_info=delivery_info
    )

    # 주문과 카트 아이템들 연결 및 카트 상태 변경
    for cart in cart_list:
        order_cart = OrderCart.objects.create(
            order=order,
            cart=cart
        )
        # 카트 상태를 변경하여 주문에 연결되었음을 표시
        cart.status = True
        cart.save()

    URL = 'https://kapi.kakao.com/v1/payment/approve'
    headers = {
        "Authorization": "KakaoAK " + admin_key,
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",    # 테스트용 코드
        "tid": request.session['tid'],  # 결제 요청시 세션에 저장한 tid
        "partner_order_id": "{}".format(order.id),     # 주문번호
        "partner_user_id": "{}".format(user),    # 유저 아이디
        "pg_token": request.GET.get("pg_token"),     # 쿼리 스트링으로 받은 pg토큰
    }

    res = requests.post(URL, headers=headers, params=params)
    res = res.json()
    context = {
        'res': res,
        'order':order,
        'cart_list':cart_list,
    }
    
    # 세션에서 delivery_info 및 total_price 제거
    if 'delivery_info' in request.session:
        del request.session['delivery_info']
    if 'total_price' in request.session:
        del request.session['total_price']
        
    return render(request, 'payment/paysuccess.html', context)
    
def payfail(request):
    return render(request, 'payment/payfail.html')
def paycancel(request):
    return render(request, 'payment/paycancel.html')

def cart_delete(request):
    if request.method == 'GET':
        checkbox_item = request.GET.getlist('checkbox')

        # checkbox_item = request.POST.get('checkbox', '').split(',')
        # checkbox_item = [check for check in checkbox_item if check]
                

        for check in checkbox_item:   
            try:
                # 만약 check가 숫자가 아니라면 ValueError가 발생
                check = int(check)   
            except ValueError: 
                print('선택된 상품이 없습니다.')

            check_item = Cart.objects.get(user=request.user, item=check, status=False) 
            check_item.delete()

    return redirect('cart:cart_detail')