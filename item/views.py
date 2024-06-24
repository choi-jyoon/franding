from django.shortcuts import render, redirect
from django.views.generic import ListView,DetailView
from django.views.generic import FormView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from django.db.models import Q,Count,Prefetch
from .models import *
from cart.models import Cart
from review.models import *
from QnA.models import FAQ
from item.models import Item
from django.shortcuts import get_object_or_404

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.decorators import login_required

import redis
import time
from django.core.cache import cache
from django_redis import get_redis_connection
from django.utils import timezone
from .models import Item, ItemViewCount
from datetime import timedelta
from django.http import HttpResponseBadRequest
from django.db.models import Count, Sum


def list_item(request):

    items= Item.objects.order_by('name','size').distinct('name')
    # 체크박스 필터링 기능 추가
    category1_ids = request.GET.getlist('cat1')
    category2_ids = request.GET.getlist('cat2')
    category3_ids = request.GET.getlist('brand')
    category4_ids = request.GET.getlist('item_type')

    if category1_ids:
        items = items.filter(cat1__id__in=category1_ids)
    if category2_ids:
        items = items.filter(cat2__id__in=category2_ids)
    if category3_ids:
        items = items.filter(brand__id__in=category3_ids)
    if category4_ids:
            items = items.filter(item_type__id__in=category4_ids)
    if request.path == '/item/perfume/':
        items = items.filter(item_type__id__in= ['1'])
    elif request.path == '/item/other/':
        items = items.exclude(item_type__id__in=['1'])
    #price 필터링
    price_filters = request.GET.getlist('price')
    if '1' in price_filters:
        items = items.filter(price__gte=0, price__lte=70000)
    if '2' in price_filters:
        items = items.filter(price__gte=70000, price__lte=150000)
    if '3' in price_filters:
        items = items.filter(price__gte=150000, price__lte=220000)
    if '4' in price_filters:
        items = items.filter(price__gte=220000)


    show_note = bool(request.path != '/item/brand/')
    show_type = bool(request.path != '/item/perfume/')



    paginator = Paginator(items, 9)  # 한 페이지에 20개씩 표시
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    if request.path == '/item/other/':
        context = {
        'item':Item.objects.all(),
        'show_cat':False,
        'items': page_obj,
        'cat1': Category1.objects.all(),
        'cat2': Category2.objects.all(),
        'brand':Brand.objects.all(),
        'item_type':ItemType.objects.exclude(id=1),
        'selected_cat1':[int(cat_id) for cat_id in category1_ids],
        'selected_cat2':[int(cat_id) for cat_id in category2_ids],
        'selected_brand':[int(cat_id) for cat_id in category3_ids],
        'selected_type':[int(cat_id) for cat_id in category4_ids],
        'show_note':show_note,
        'show_type':show_type,
        'selected_price':request.GET.getlist('price'),
        'page':page_number,
        }
    else:    
        context = {
        'items': page_obj,
        'cat1': Category1.objects.all(),
        'cat2': Category2.objects.all(),
        'brand':Brand.objects.all(),
        'item_type':ItemType.objects.all(),
        'selected_cat1':[int(cat_id) for cat_id in category1_ids],
        'selected_cat2':[int(cat_id) for cat_id in category2_ids],
        'selected_brand':[int(cat_id) for cat_id in category3_ids],
        'selected_type':[int(cat_id) for cat_id in category4_ids],
        'show_note':show_note,
        'show_type':show_type,
        'selected_price':request.GET.getlist('price'),
        'page':page_number
        }
    return render(request, 'item/list.html', context)


def detail_list_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    sort_by = request.GET.get('sort_by', '-datetime')
    reviews = Review.objects.filter(item=item_id).annotate(likes_count=Count('reviewlike')).order_by('-datetime').prefetch_related(
        Prefetch('reviewreply_set', queryset=ReviewReply.objects.order_by('-datetime'))
    )
    if sort_by == '-datetime':
        reviews = Review.objects.filter(item=item_id).annotate(likes_count=Count('reviewlike')).order_by('-datetime').prefetch_related(
        Prefetch('reviewreply_set', queryset=ReviewReply.objects.order_by('-datetime')))
    elif sort_by == '-star':
        reviews = Review.objects.filter(item=item_id).annotate(likes_count=Count('reviewlike')).order_by('-star').prefetch_related(
        Prefetch('reviewreply_set', queryset=ReviewReply.objects.order_by('-datetime')))
    elif sort_by == '-likes':
        # 리뷰를 좋아요 수 순으로 정렬
        reviews = Review.objects.filter(item=item_id).annotate(likes_count=Count('reviewlike')).order_by('-likes_count').prefetch_related(
            Prefetch('reviewreply_set', queryset=ReviewReply.objects.order_by('-datetime')))
    paginator = Paginator(reviews, 3)
    faqs = FAQ.objects.all()  


    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)    
    
    if page_obj:
        context = {
        "item":item,
        "review":page_obj,
        'faqs':faqs,
        'sort_by':sort_by,
        }
    else:
        context = {
            "item":item,
            'message': '리뷰가 없습니다.',
            'faqs':faqs,
            'sort_by':sort_by,
        }    
    return render(request,'item/detail.html',context) 


@login_required
def    add_cart(request,item_id):
    item=Item.objects.get(id=item_id)
    context={
        "item":item
    }
    if request.method == 'POST':
        item = Item.objects.get(id=item_id)
        user = request.user
        
        # 장바구니에 동일한 상품이 있는지 확인
        cart_item = Cart.objects.filter(user=user, item=item,status=False).first()
        if cart_item and cart_item.status is False:
            # 있다면 수량 증가
            cart_item.amount = cart_item.amount +int(request.POST['current-amount'])
            cart_item.save()
            context={
            "item":item

            }
        else:
            # 없다면 새로 생성
            Cart.objects.create(user=user, item=item, amount=int(request.POST['current-amount']))
            context={
            "item":item

            }
        if int(request.POST['go_cart']) == 1:
            return redirect(request.path)
        elif int(request.POST['go_cart']) == 0:
            return redirect('cart:cart_detail')
    else:
        return render(request,'item/detail.html',context) 


@login_required
@csrf_protect
def like_review(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            review_id = request.POST.get('review_id')
            review = get_object_or_404(Review, id=review_id)
            user = request.user

            if ReviewLike.objects.filter(review=review, user=user).exists():
                ReviewLike.objects.filter(review=review, user=user).delete()
                liked = False
            else:
                ReviewLike.objects.create(review=review, user=user)
                liked = True

            likes_count = review.reviewlike_set.count()
            return JsonResponse({'liked': liked, 'likes_count': likes_count})
        except Exception as e:
           
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def check_like_status(request, review_id):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            review = get_object_or_404(Review, id=review_id)
            user = request.user
            liked = ReviewLike.objects.filter(review=review, user=user).exists()
            return JsonResponse({'liked': liked})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)



@login_required
def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    is_liked = item.is_liked_by_user(request.user)
    return render(request, 'item/item_detail.html', {'item': item, 'is_liked': is_liked})

@login_required
def toggle_like(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    like, created = Like.objects.get_or_create(user=request.user, item=item)

    if not created:  # 이미 좋아요가 눌려져 있는 경우
        like.delete()  # 좋아요 취소
        return JsonResponse({"liked": False, "count": item.like_set.count()})

    return JsonResponse({"liked": True, "count": item.like_set.count()})


# Redis 연결 설정 (모듈 수준에서 한 번만 설정) / 기능보류!
cache = get_redis_connection("default")

# 접속자 관리 함수
def add_viewer(item_id, session_id):
    key = f'item_{item_id}_viewers'  # Redis 키 설정
    current_time = int(time.time())  # 현재 시간 (초 단위)
    expire_time = 300  # 만료 시간 (5분)
    cache.zadd(key, {session_id: current_time})  # 접속자 추가 (세션 ID와 현재 시간)
    cache.expire(key, expire_time)  # 키 만료 시간 설정

def remove_expired_viewers(item_id):
    key = f'item_{item_id}_viewers'  # Redis 키 설정
    current_time = int(time.time())  # 현재 시간 (초 단위)
    cache.zremrangebyscore(key, 0, current_time - 300)  # 5분 이상 비활성 접속자 제거

def get_current_viewers(item_id):
    key = f'item_{item_id}_viewers'  # Redis 키 설정
    remove_expired_viewers(item_id)  # 만료된 접속자 제거
    return cache.zcard(key)  # 현재 접속자 수 반환

def update_daily_view_count(item_id):
    today = timezone.now().date()
    view_count, created = ItemViewCount.objects.get_or_create(item_id=item_id, date=today)
    view_count.count = models.F('count') + 1  # 더 효율적인 업데이트
    view_count.save(update_fields=['count'])

def detail_list_item(request, item_id):
    # 상품 객체 가져오기
    item = get_object_or_404(Item, id=item_id)
    
    # 사용자 세션 ID 가져오기
    session_id = request.session.session_key  
    if not session_id:
        request.session.create()  # 세션이 없으면 세션 생성
        session_id = request.session.session_key  # 생성된 세션 ID 가져오기
    
    # 접속자 추가 및 현재 접속자 수 가져오기
    add_viewer(item_id, session_id)
    update_daily_view_count(item_id)  # 일별 조회수 업데이트
    current_viewers = get_current_viewers(item_id)
    
    # 리뷰 가져오기 및 정렬
    reviews = Review.objects.filter(item=item_id).annotate(likes_count=Count('reviewlike')).order_by('-datetime').prefetch_related(
        Prefetch('reviewreply_set', queryset=ReviewReply.objects.order_by('-datetime'))
    )
    
    # 페이징 처리
    paginator = Paginator(reviews, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # FAQ 가져오기
    faqs = FAQ.objects.all()  

    # context 구성
    context = {
        "item": item,
        "current_viewers": current_viewers,
        'faqs': faqs,
    }
    
    if page_obj:
        context["review"] = page_obj
    else:
        context['message'] = '리뷰가 없습니다.'

    return render(request, 'item/detail.html', context)

# 특정 기간 동안의 조회수를 집계하고 정렬하는 로직
def get_top_items(period_days):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period_days)
    top_items = ItemViewCount.objects.filter(date__range=(start_date, end_date)) \
                                     .values('item') \
                                     .annotate(total_views=Sum('count')) \
                                     .order_by('-total_views')
    return top_items

def item_list(request):
    sort_by = request.GET.get('sort_by', 'default')
    items = Item.objects.all()
    
    if sort_by == 'week':
        top_items = get_top_items(7)
        item_ids = [item['item'] for item in top_items]
        items = Item.objects.filter(id__in=item_ids).annotate(total_views=Sum('itemviewcount__count')).order_by('-total_views')
    elif sort_by == 'month':
        top_items = get_top_items(30)
        item_ids = [item['item'] for item in top_items]
        items = Item.objects.filter(id__in=item_ids).annotate(total_views=Sum('itemviewcount__count')).order_by('-total_views')
    elif sort_by == 'half_year':
        top_items = get_top_items(180)
        item_ids = [item['item'] for item in top_items]
        items = Item.objects.filter(id__in=item_ids).annotate(total_views=Sum('itemviewcount__count')).order_by('-total_views')
    
    # 페이징 처리
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'items': page_obj,
        'sort_by': sort_by,
    }

    return render(request, 'item/list.html', context)



# 조회수 수정 버전
# # 상품 상세 페이지 뷰 함수
# def product_detail(request, item_id):
#     item = get_object_or_404(Item, id=item_id)  # 상품 객체 가져오기
#     session_id = request.session.session_key  # 사용자 세션 ID 가져오기

#     if not session_id:
#         request.session.create()  # 세션이 없으면 세션 생성
#         session_id = request.session.session_key  # 생성된 세션 ID 가져오기

#     add_viewer(item_id, session_id)  # 접속자 추가
#     current_viewers = get_current_viewers(item_id)  # 현재 접속자 수 가져오기

#     return render(request, 'item/detail.html', {
#         'item': item,
#         'current_viewers': current_viewers
#     })

# def detail_list_item(request, item_id):
#     # 상품 객체 가져오기
#     item = get_object_or_404(Item, id=item_id)
    
#     # 사용자 세션 ID 가져오기
#     session_id = request.session.session_key  
#     if not session_id:
#         request.session.create()  # 세션이 없으면 세션 생성
#         session_id = request.session.session_key  # 생성된 세션 ID 가져오기
    
#     # 접속자 추가 및 현재 접속자 수 가져오기
#     add_viewer(item_id, request.session.session_key)
#     current_viewers = get_current_viewers(item_id)
    
#     # 리뷰 가져오기 및 정렬
#     reviews = Review.objects.filter(item=item_id).annotate(likes_count=Count('reviewlike')).order_by('-datetime').prefetch_related(
#         Prefetch('reviewreply_set', queryset=ReviewReply.objects.order_by('-datetime'))
#     )
    
#     # 페이징 처리
#     paginator = Paginator(reviews, 3)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     # FAQ 가져오기
#     faqs = FAQ.objects.all()  

#     # context 구성
#     context = {
#         "item": item,
#         "current_viewers": current_viewers,
#         'faqs': faqs,
#     }
    
#     if page_obj:
#         context["review"] = page_obj
#     else:
#         context['message'] = '리뷰가 없습니다.'

#     return render(request, 'item/detail.html', context)