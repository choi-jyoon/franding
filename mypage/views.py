from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from cart.models import OrderCart, Order, PayInfo, Refund
from .models import UserAddInfo
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from QnA.models import Question
from item.models import Item
from django.http import JsonResponse
from django.db.models import Count, Prefetch
from django.utils import timezone
from payment.models import Delivery, Coupon, UserCoupon
from django.db.models import Q
import requests
import os
from dotenv import load_dotenv
import boto3

load_dotenv()
admin_key = os.getenv('admin_key')


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


@login_required
def order_index(request):    
    # orders = Order.objects.filter(ordercart__cart__user=request.user).order_by('-datetime').distinct().prefetch_related('ordercart_set__cart__item')
    orders = Order.objects.filter(ordercart__cart__user=request.user).order_by('-datetime').distinct().prefetch_related(
        Prefetch(
            'ordercart_set',
            queryset=OrderCart.objects.only('id', 'cart__item__id', 'cart__item__name', 'cart__item__image')
                .select_related('cart__item')
        )
    ).only('id', 'datetime', 'total_price')
    
    paginator = Paginator(orders, 4)  # 한 페이지당 4개의 주문을 보여줍니다.
    
    # URL의 'page' GET 파라미터로부터 페이지 번호를 가져옵니다. 기본값은 1입니다.
    page_number = request.GET.get('page', 1)
    # 해당 페이지의 주문 객체를 가져옵니다.
    page_obj = paginator.get_page(page_number)
    
    if page_obj:
        context = {
            'orders': page_obj,          
        }
    else:
        context = {
            'message': '주문 내역이 없습니다.'
        }
    return render(request, 'mypage/order_index.html', context)

@login_required
def order_detail(request, pk):
    order = Order.objects.get(pk=pk)
    ordercarts = OrderCart.objects.filter(order_id = pk)
    context={
        'order' : order,
        'ordercarts':ordercarts
    }
    return render(request, 'mypage/order_detail.html', context)

@login_required
def order_confirm(request, pk):
    try:
        ordercart = OrderCart.objects.get(id=pk)
        ordercart.status = 1
        ordercart.save()
        return redirect('mypage:order_detail', ordercart.order.id)
    except OrderCart.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'OrderCart not found'}, status=404)
    
@login_required
def refund_confirm(request, pk):
    
    refund_item = OrderCart.objects.get(id = pk)
    total_price = refund_item.cart.item.price * refund_item.cart.amount
    userinfo = UserAddInfo.objects.get(user=request.user)
    
    # 확인 버튼 클릭 시 환불 완료 상태로 변화
    if request.method == 'POST':
        refund_item.status = 3
        refund_item.save()
    
        # 세션에 배송 정보 저장
        request.session['delivery_info'] = {
            'receiver': request.POST.get('receiver'),
            'receiver_postcode': request.POST.get('receiver_postcode'),
            'receiver_address': request.POST.get('receiver_address'),
            'receiver_detailAddress': request.POST.get('receiver_detailAddress'),
            'receiver_extraAddress': request.POST.get('receiver_extraAddress'),
            'receiver_phone': request.POST.get('receiver_phone'),
            'receiver_email': request.POST.get('receiver_email')
        }

        # 세션에서 배송 정보 읽기
        deliveryinfo_session = request.session.get('delivery_info')

        # 배송 정보 생성
        delivery_info = Delivery.objects.create(
            status = 3,
            receiver=deliveryinfo_session['receiver'],
            receiver_postcode=deliveryinfo_session['receiver_postcode'],
            receiver_address=deliveryinfo_session['receiver_address'],
            receiver_detailAddress=deliveryinfo_session['receiver_detailAddress'],
            receiver_extraAddress=deliveryinfo_session['receiver_extraAddress'],
            receiver_phone=deliveryinfo_session['receiver_phone'],
            receiver_email=deliveryinfo_session['receiver_email']
        )
        
        return redirect('mypage:order_detail', refund_item.order.id)
    
    context = {
        'item_list': [refund_item.cart],
        'total_price': -total_price,
        'shipping_fee' : 0,
        'userinfo' : userinfo,
        'refund_item': refund_item
    }
    return render(request, 'mypage/refund_info.html', context)
    
@login_required
def order_refund(request, pk):
    try:
        ordercart = OrderCart.objects.get(id=pk)
        ordercart.status = 2
        ordercart.save()
        # refund 로직 
        user = request.user 
        pay_info = PayInfo.objects.get(order = ordercart.order)
        
        tid = pay_info.tid 
        
        cancel_amount = ordercart.cart.item.price * ordercart.cart.amount
        cancel_available_amount = ordercart.order.total_price - cancel_amount
        # 결제 취소 요청 로직
        URL = 'https://open-api.kakaopay.com/online/v1/payment/cancel'
        headers = {
            "Authorization": "KakaoAK " + admin_key,
            "Content-type": "application/json",
        }
        params = {
            "cid": "TC0ONETIME",    # 테스트용 코드
            "tid": tid,  # 결제 요청시 세션에 저장한 tid
            "cancel_amount": cancel_amount, # 취소 요청 금액
            "cancel_tax_free_amount": 0,
            "cancel_vat_amount": 0,
            "cancel_available_amount": cancel_available_amount,     #남은 취소 가능 금액 
        }

        res = requests.post(URL, headers=headers, params=params)
        res = res.json()
        
        # PayInfo 정보 업데이트
        pay_info.status = "cancelled"
        pay_info.canceled_at = timezone.now()
        pay_info.save()
        
        # OrderCart 상태 업데이트
        ordercart.status = 2 
        ordercart.save()
        
        # 환불 정보 생성
        refund = Refund.objects.create(
            ordercart = ordercart,
            price = cancel_amount,
        )
            
        return redirect('mypage:order_detail', ordercart.order.id)
    except OrderCart.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'OrderCart not found'}, status=404)

@login_required
def user_info(request):
    try:
        user_info = UserAddInfo.objects.get(user=request.user)
        context={
            'object':user_info
        }
    except:
        context = {
            'message':'회원 정보를 입력해주세요.' 
        }
    return render(request, 'mypage/user_info.html', context)

@login_required
def add_user_info(request):
    user=request.user
    
    try:
        user_add_info = UserAddInfo.objects.filter(user=user).first()
    except UserAddInfo.DoesNotExist:
        user_add_info = None
    
    if user_add_info != None: 
        
        return redirect('mypage:user_info')
    else:
        # get
        if request.method=='GET':
            return render(request, 'mypage/add_user_info.html')
        # post
        elif request.method=='POST':
            # 폼에서 전달되는 각 값을 뽑아와서 DB에 저장
            user = request.user
            user_address = request.POST['address']
            user_phone = request.POST['phone']
            
            # 파일 업로드가 있는지 확인
            if 'file' in request.FILES:
                # 이미지 저장 및 url 설정 내용
                fs = FileSystemStorage()
                uploaded_file = request.FILES['file']
                name = fs.save(uploaded_file.name, uploaded_file)
                url = fs.url(name)
                
                s3.upload_file(os.path.join(settings.MEDIA_ROOT, name), 'franding', name)
                
            else:
                url = None  # 파일이 없을 경우 None으로 설정
            
            UserAddInfo.objects.create(user=user, address=user_address, phone=user_phone, profile_img = url)
            # 회원가입 쿠폰 지급 
            coupons = Coupon.objects.filter(Q(name__icontains='회원가입'))
            for coupon in coupons : 
                user_coupon = UserCoupon.objects.create(
                    user = user,
                    coupon = coupon
                )

            return redirect('mypage:user_info')
    
@login_required
def update_user_info(request):
    user=request.user
    # get
    if request.method == 'GET':
        user_info = UserAddInfo.objects.get(user=request.user)
        context = {
            'object': user_info
        }
        return render(request, 'mypage/update_user_info.html', context)
    # post
    elif request.method == 'POST':
        # 폼에서 전달되는 각 값을 뽑아와서 DB에 저장
        user_info = UserAddInfo.objects.get(user=request.user)
        user_info.phone = request.POST['phone']
        user_info.address = request.POST['address']
        user_info.postcode = request.POST['postcode']
        user_info.detailAddress = request.POST['detailAddress']
        user_info.extraAddress = request.POST['extraAddress']
        
        user.last_name = request.POST['last_name']
        user.first_name = request.POST['first_name']
        user.email = request.POST['email']
        
        # 이미지 업데이트 처리
        if 'file' in request.FILES:
            fs = FileSystemStorage()
            uploaded_file = request.FILES['file']
            name = fs.save(uploaded_file.name, uploaded_file)
            url = fs.url(name)
            user_info.profile_img = url
            
            s3.upload_file(os.path.join(settings.MEDIA_ROOT, name), 'franding', name)
            
            
        user_info.save()
        user.save()

        return redirect('mypage:user_info')
    
@login_required
def user_delete(request):
    request.user.delete()
    auth_logout(request)
    return redirect('home')

@login_required
def user_coupon(request):
    coupons = UserCoupon.objects.filter(user = request.user)
    context = {
        'coupons' : coupons,
    }
    return render(request, 'mypage/user_coupon.html', context)