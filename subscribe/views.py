from django.shortcuts import render, redirect
from .models import Keyword, Subscribe, SubscribeKeyword
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from collections import defaultdict, Counter
from item.models import Item
from mypage.models import UserAddInfo
import random
# Create your views here.

@login_required
def index(request):
    
    now = timezone.now()
    
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
def payment_process(request):
    user_info = UserAddInfo.objects.get(user=request.user)
    
    if request.method == 'POST':
        # 실제 결제 처리 로직 구현
        
        
        # 결제 성공 시
        user_info.membership = True
        user_info.save()
        return redirect('membership')
    
    shipping_fee = 3000
    subscribe_item = [
        {
            'item': {
                'name': 'franding membership'
            },
            'size': {
                'ml': '-'
            },
            'amount': 1,
            'sub_total': 15900
        }
    ]
    context = {
        'item_list': subscribe_item,
        'total_price': 15900,
        'shipping_fee': 0,
        'userinfo': user_info
    }
    return render(request, 'payment/payment_info.html', context)


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
