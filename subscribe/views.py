from django.shortcuts import render, redirect
from .models import Keyword, Subscribe, SubscribeKeyword, SubscribePayInfo
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from collections import defaultdict, Counter
from item.models import Item
from mypage.models import UserAddInfo
import random
import requests
import os
from dotenv import load_dotenv
# from .tasks import process_recurring_payments

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
# Create your views here.

@login_required
def index(request):
    
    now = timezone.now()
    
    # 구독 키워드 신청 
    if request.method == 'POST':
        selected_keywords = request.POST.get('selected_keywords')
        keyword_id = selected_keywords.split(',') if selected_keywords else []
        
        subscribe = Subscribe(user = request.user)
        subscribe.save()
        
        for id in keyword_id:
            subscribe_keyword = SubscribeKeyword(keyword = Keyword.objects.get(pk=id), subscribe=subscribe)
            subscribe_keyword.save()

    keyword_objects = Keyword.objects.filter(month__year = now.year, month__month = now.month)
    subscribe_objects = SubscribeKeyword.objects.filter(subscribe__user = request.user)
    is_subscribed = request.user.subscribe_set.filter(datetime__year = now.year, datetime__month = now.month).exists()
    
    # subscribe ID를 키로, keyword 리스트를 값으로 가지는 딕셔너리
    subscriptions = defaultdict(list)

    for sub_keyword in subscribe_objects:
        # subscribe ID를 키로 사용하여 keyword 추가
        subscriptions[sub_keyword.subscribe].append(sub_keyword.keyword.word)
        
    subscriptions = dict(subscriptions)
    context = {
        'keywords': keyword_objects,
        'date': now,
        'subscribes' : subscriptions,
        'is_subscribed': is_subscribed
    }
    return render(request, 'subscribe/index.html', context)


@login_required
def membership(request):
    user_info = UserAddInfo.objects.get(user = request.user)
    
    # 멤버십 없는 유저는 멤버십 신청화면으로 이동
    if user_info.membership == False :
        if request.method == 'POST':
            return redirect('subscribe:payment')
        return render(request, 'subscribe/membership.html')
    return index(request)

@login_required
def first_pay_process(request):

    user_info = UserAddInfo.objects.get(user=request.user)
    current_domain = request.get_host()
    
    if request.method == 'POST':
        # 실제 결제 요청 로직 구현
        
        url = "https://open-api.kakaopay.com/online/v1/payment/ready"
        headers = {
            "Authorization": f"SECRET_KEY {SECRET_KEY}",
            'Content-Type':'application/json',
        }
        
        data = {
            "cid": "TCSUBSCRIP",    # 테스트용 코드 (정기결제용 cid)
            "partner_order_id": "1001",     # 주문번호
            "partner_user_id": "{}".format(request.user),    # 유저 아이디
            "item_name": "franding membership",        # 구매 물품 이름
            "quantity": "1",                # 구매 물품 수량
            "total_amount": "15900",        # 구매 물품 가격
            "tax_free_amount": "0",         # 구매 물품 비과세
            'approval_url':f'http://{current_domain}/subscribe/paysuccess', 
            'fail_url':f'http://{current_domain}/subscribe/payfail',
            'cancel_url':f'http://{current_domain}/subscribe/paycancel'
        }
        
        response = requests.post(url, headers= headers, json=data)
        request.session['tid'] = response.json()['tid']     # 결제 승인시 사용할 tid 세션에 저장
        next_url = response.json()['next_redirect_pc_url']  # 결제 페이지로 넘어갈 url
        
        SubscribePayInfo.objects.create(
            user=request.user,
            tid=request.session['tid'],
            cid="TCSUBSCRIP",
            payment_method_type ="MONEY",
            item_name="franding membership",
            quantity=1,
            total_amount=15900,
            status='prepared'  # 결제 준비 상태로 저장
        )
        return redirect(next_url)
    
    
    
    shipping_fee = 3000
    subscribe_item = [
        {
            'item': {
                'name': 'franding membership'
            },

            'sub_total': 15900
        }
    ]
    context = {
        'item_list': subscribe_item,
        'total_price': 15900,
        'shipping_fee': 300,
        'userinfo': user_info
    }
    return render(request, 'subscribe/regular_pay.html', context)


@login_required
def pay_success(request):
    # 결제 처리 로직
    now = timezone.now()
    tid = request.session.get('tid')
    if tid:
        # 카카오페이 결제 승인 API 호출
        url = f'https://open-api.kakaopay.com/online/v1/payment/approve'
        headers = {
            "Authorization": f"SECRET_KEY {SECRET_KEY}",
            'Content-Type':'application/json',
        }
        data = {
            "cid": "TCSUBSCRIP",    # 테스트용 코드 (정기결제용 cid)
            "tid": tid,
            "partner_order_id": "1001",     # 주문번호
            "partner_user_id": "{}".format(request.user),    # 유저 아이디
            "pg_token": request.GET.get('pg_token')  # 결제 승인시 전달되는 pg_token
        }
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        
        if response.status_code == 200:
            sid = response_data.get('sid')
            payment_info = SubscribePayInfo.objects.get(tid=tid, user=request.user)
            payment_info.status = 'approved'  # 결제 완료 상태로 변경
            payment_info.approved_at = now  # 승인 시간 업데이트
            payment_info.last_payment_date = now
            payment_info.next_payment_date = now + timedelta(days=30)
            if sid:
                payment_info.sid = sid  # sid 값 저장
            payment_info.save()
            
            # 결제 완료 후 처리할 로직 추가 (예: 구독 활성화)
            user_info = UserAddInfo.objects.get(user=request.user)
            user_info.membership = True
            user_info.save()
            
            # 세션에서 tid 제거
            del request.session['tid']
            
            # process_recurring_payments.delay(request.user.id)
            
            # index 함수 호출
            return index(request)

    return render(request, 'payment/payfail.html')

@login_required
def second_pay_process(request):
    # 2회차 이후 정기결제 로직 
    now = timezone.now()
    pay_info = SubscribePayInfo.objects.get(user=request.user, next_payment_date__lte=now, status='approved')
    
    # 정기 결제 처리 로직 구현
    
    url = "https://open-api.kakaopay.com/online/v1/payment/subscription"
    headers = {
        "Authorization": f"SECRET_KEY {SECRET_KEY}",
        'Content-Type':'application/json',
    }
    data = {
        "cid": "TCSUBSCRIP",    # 테스트용 코드 (정기결제용 cid)
        "sid": pay_info.sid,
        "partner_order_id": "1002",     # 주문번호
        "partner_user_id": "{}".format(request.user),    # 유저 아이디
        "item_name": "franding membership",        # 구매 물품 이름
        "quantity": "1",                # 구매 물품 수량
        "total_amount": "15900",        # 구매 물품 가격
        "tax_free_amount": "0",         # 구매 물품 비과세
    }
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    
    if response.status_code == 200:
        # n회차 결제 성공 -> 구독 정보 업데이트
        pay_info.next_payment_date = now + timedelta(days=30)  # 다음 결제 날짜를 30일 뒤로 설정
        pay_info.last_payment_date = now  # 마지막 결제일을 현재 시간으로 설정
        pay_info.save()
        return JsonResponse({'status': 'success', 'message': '구독 갱신이 완료되었습니다.'})
    
    return render(request, 'payment/payfail.html')

@login_required
def pay_fail(request):
    # 결제 실패 후 처리 로직
    return render(request, 'payment/payfail.html')

@login_required
def pay_cancel(request):
    # 정기결제 비활성화 
    pay_info = SubscribePayInfo.objects.filter(user = request.user).order_by('-id').first()
    if request.method == 'POST':
        url = f'https://open-api.kakaopay.com/online/v1/payment/manage/subscription/inactive'
        headers = {
            "Authorization": f"SECRET_KEY {SECRET_KEY}",
            'Content-Type':'application/json',
        }
        data = {
            "cid": "TCSUBSCRIP",    # 테스트용 코드 (정기결제용 cid)
            "sid": pay_info.sid,
        }
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        
        pay_info.status = 'INACTIVE'  # 결제 완료 상태로 변경
        pay_info.inactivated_at = timezone.now()  # 승인 시간 업데이트

        pay_info.save()
            
        # 해지 완료 후 구독 비활성화
        user_info = UserAddInfo.objects.get(user=request.user)
        user_info.membership = False
        user_info.save()
        
    return render(request, 'subscribe/membershipcancel.html')


@login_required
def detail(request, pk):
    
    subscribe = Subscribe.objects.get(pk=pk)
    sub_keywords = SubscribeKeyword.objects.filter(subscribe=subscribe)
    
    # 키워드별로 카테고리 1, 2 리스트 저장
    cat1 = []
    cat2 = []
    for sub_keyword in sub_keywords:
        cat1.append(sub_keyword.keyword.category1)
        cat2.append(sub_keyword.keyword.category2)
    
    # 가장 많이 나온 값 선택
    most_cat1 = Counter(cat1).most_common(1)[0][0]
    most_cat2 = Counter(cat2).most_common(1)[0][0]
    
    # 가장 많이 나온 카테고리에 맞는 아이템 선정
    items = Item.objects.filter(cat1 = most_cat1, cat2 = most_cat2, item_type = '1')
    if items.exists():
        item = random.choice(items)
    # 카테고리에 맞는 아이템 없을 시 카테고리1만 고려해서 랜덤 선택
    else:
        item = random.choice(Item.objects.filter(cat1 = most_cat1, item_type = '1'))
        
    subscribe.item = item
    subscribe.save()
    
    context = {
        'subscribe_object':subscribe,
        'subscriptions' : sub_keywords,
    }
    return render(request, 'subscribe/detail.html', context)

@login_required
def membership_detail(request):
    # 멤버십 상세 페이지 
    membership_info = SubscribePayInfo.objects.filter(user = request.user)
    context = {
        'memberships' : membership_info
    }
    return render(request, 'subscribe/membership_detail.html', context)