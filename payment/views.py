from django.shortcuts import render, redirect, get_object_or_404
from cart.models import Cart, Order, OrderCart, PayInfo
from mypage.models import UserAddInfo
from .models import Delivery, UserCoupon
import requests
import os
from dotenv import load_dotenv
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponse
# from time_logger import time_logger

load_dotenv()
admin_key = os.getenv('admin_key')

# @time_logger(category='payment_list')
# 0.6695785522460938초
def payment_list(request, total_price=0):
    current_domain = request.get_host()
    template_name = 'payment/payment_info.html'
    user=request.user
    cnt = 0
    total_amount = 0
    check_item_list = []

    coupons = UserCoupon.objects.filter(user = user, is_used = False)

    if request.method == 'GET': # True
        if 'check-item' not in request.GET:
            messages.warning(request, '상품을 1개 이상 주문하셔야 합니다.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            checkbox_item = request.GET.getlist('check-item') 
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

        if check_item.item.inventory == 0:  # 상품 재고가 0인지 확인합니다.
            messages.warning(request, '재고가 없는 상품이 있습니다.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))  # 재고가 없으면 결제를 중단합니다.
        
        check_item_list.append(check_item)
        total_price += (check_item.item.price * check_item.amount)
            
        
        # 잠깐 주석처리
        cnt += 1
        # total_price += (check_item.item.price * check_item.amount)  # 총 가격
        total_amount += check_item.amount  # 총 수량
        item_name = check_item.item.name # 대표 구매 물품 이름
    if cnt > 1:
        item_name += '외 {}건'.format(cnt-1) 

    # 배송비
    if total_price < 50000:
        shipping_fee = 3000
        total_price += shipping_fee
    else:
        shipping_fee = 0    
                          
           
    # 세션에서 total_price를 초기화 (결제 페이지에 처음 들어왔을 때만)
    if 'initial_visit' not in request.session:
        request.session['total_price'] = 0
        request.session['initial_visit'] = True
    else:
        if 'total_price' in request.session:
            total_price = request.session['total_price']
        # 두 번째 방문 시 'initial_visit'을 삭제
        del request.session['initial_visit']
            
            
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
        
        request.session['initial_visit'] = True
        del request.session['initial_visit'] 
        return redirect(next_url)
    
    context = {
            'item_list': check_item_list,
            'total_price': total_price,
            'shipping_fee' : shipping_fee,
            'userinfo' : userinfo,
            'coupons': coupons,
    }
    
    return render(request, template_name, context)
        

def paysuccess(request):
    user=request.user
    cart_list = []
    deliveryinfo_session = request.session.get('delivery_info')
    total_price = request.session.get('total_price')
    user_coupon_id = request.session.get('user_coupon_id')
    
    if user_coupon_id:
        user_coupon = UserCoupon.objects.get(id=user_coupon_id)
        user_coupon.is_used = True
        user_coupon.save()
    
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
    
    # 결제 정보 PayInfo 에 저장
    pay_info = PayInfo.objects.create(
        user=request.user,
        tid=request.session['tid'],
        cid="TC0ONETIME",
        payment_method_type ="MONEY",
        order=order,
        total_amount=total_price,
        status='approved'  # 결제 준비 상태로 저장
    )
    
    # 세션에서 delivery_info 및 total_price 제거
    if 'delivery_info' in request.session:
        del request.session['delivery_info']
    if 'total_price' in request.session:
        del request.session['total_price']
    if 'initial_visit' in request.session:
        del request.session['initail_visit']
        
    return render(request, 'payment/paysuccess.html', context)
    
def payfail(request):
    return render(request, 'payment/payfail.html')

def paycancel(request):
    if 'total_price' in request.session:
        del request.session['total_price']
    if 'initial_visit' in request.session:
        del request.session['initail_visit']
    return render(request, 'payment/paycancel.html')

def apply_coupon(request):
    if request.method == 'POST':
        try:
            user_coupon_id = request.POST.get('coupon_id')
            request.session['user_coupon_id'] = user_coupon_id
            user_coupon = get_object_or_404(UserCoupon, id=user_coupon_id)
            total_price = float(request.POST.get('total_price'))  # 문자열을 float로 변환
            
            discount_amount = user_coupon.coupon.discount_rate * 0.01 * total_price
            new_total_price = int(total_price - discount_amount)  # 정수로 변환
            request.session['total_price'] = new_total_price  # 세션에 저장
            return JsonResponse({'new_total_price': new_total_price})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=400)