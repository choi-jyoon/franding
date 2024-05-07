from django.shortcuts import render
from .models import Keyword, Subscribe, SubscribeKeyword
from django.utils import timezone
from django.contrib.auth.decorators import login_required
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
    is_subscribed = request.user.subscribe_set.exists()
    
    context = {
        'keywords': keyword_objects,
        'date': now,
        'subscribes' : subscribe_objects,
        'is_subscribed': is_subscribed
    }
    return render(request, 'subscribe/index.html', context)

@login_required
def detail(request, pk):
    now = timezone.now()
    
    subscribe_objects = SubscribeKeyword.objects.get(pk=pk)
    
    context = {
        'subscribes' : subscribe_objects,
    }
    return render(request, 'subscribe/detail.html', context)