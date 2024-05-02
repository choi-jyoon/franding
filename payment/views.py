from django.shortcuts import render, redirect
from cart.models import Cart, Order, OrderCart
from mypage.models import UserAddInfo
from .models import Delivery
import requests
import os
from dotenv import load_dotenv

load_dotenv()
admin_key = os.getenv('admin_key')

# Create your views here.
def payment_list(request, total_price=0):
    template_name = 'payment/payment_info.html'

    if request.method == 'GET':
        checkbox_item = request.GET.getlist('checkbox')
        check_item_list = []
    
    for check in checkbox_item:   
        try:
            # 만약 check가 숫자가 아니라면 ValueError가 발생
            check = int(check)   
        except ValueError: 
            print('선택된 상품이 없습니다.') 
            
        check_item = Cart.objects.get(user=request.user, item=check, status=False) 
        check_item_list.append(check_item)
        total_price += (check_item.item.price * check_item.amount)        
        
    # 아이팀 결제 part
    item_list = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')
    user=request.user
    cnt = 0
    total_amount = 0
    
    try:
        userinfo = UserAddInfo.objects.get(user=request.user) # 유저정보가 있다면 가져오기
    except UserAddInfo.DoesNotExist:
        userinfo = None

    for c in item_list:
        cnt += 1
        total_price += (c.item.price * c.amount)  # 총 가격
        total_amount += c.amount  # 총 수량
        item_name = c.item.name # 대표 구매 물품 이름
    if cnt > 1:
        item_name += '외 {}건'.format(cnt-1)
           
    if request.method == "POST":
        # 배송정보를 session에 저장
        request.session['delivery_info'] = {
            'receiver': request.POST.get('receiver'),
            'receiver_address': request.POST.get('receiver_address'),
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
            'approval_url':'http://127.0.0.1:8000/payment/paysuccess', 
            'fail_url':'http://127.0.0.1:8000/payment/payfail',
            'cancel_url':'http://127.0.0.1:8000/payment/paycancel'
        }

        res = requests.post(URL, data=data, headers=headers)
        request.session['tid'] = res.json()['tid']      # 결제 승인시 사용할 tid를 세션에 저장
        next_url = res.json()['next_redirect_pc_url']   # 결제 페이지로 넘어갈 url을 저장
        return redirect(next_url)
    
    context = {
            'item_list': check_item_list,
            'total_price': total_price,
            'userinfo' : userinfo
    }
    
    return render(request, template_name, context)
        

def paysuccess(request):
    user=request.user
    cart_list = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')
    deliveryinfo_session = request.session.get('delivery_info')
    total_price = request.session.get('total_price')
    
    if not deliveryinfo_session or not total_price:
        return redirect('mypage:order_index')
    
    # 배송 정보 생성
    delivery_info = Delivery.objects.create(
        receiver=deliveryinfo_session['receiver'],
        receiver_address=deliveryinfo_session['receiver_address'],
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