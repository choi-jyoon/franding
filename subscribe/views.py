from django.shortcuts import render
from .models import Keyword, Subscribe, SubscribeKeyword
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from collections import defaultdict
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
def detail(request, pk):
    
    subscribe = Subscribe.objects.get(pk=pk)
    sub_keyword = SubscribeKeyword.objects.filter(subscribe=subscribe)
    
    context = {
        'subcribe_object':subscribe,
        'subscriptions' : sub_keyword,
    }
    return render(request, 'subscribe/detail.html', context)