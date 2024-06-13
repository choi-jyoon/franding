# item/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic import FormView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q, Count, Prefetch
from .models import Item, Category1, Category2, Brand, ItemType
from cart.models import Cart
from review.models import Review, ReviewReply, ReviewLike
from QnA.models import FAQ
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

def list_item(request):
    items = Item.objects.order_by('name', 'size').distinct('name')
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
        items = items.filter(item_type__id__in=['1'])
    elif request.path == '/item/other/':
        items = items.exclude(item_type__id__in=['1'])

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

    paginator = Paginator(items, 9)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'items': page_obj,
        'cat1': Category1.objects.all(),
        'cat2': Category2.objects.all(),
        'brand': Brand.objects.all(),
        'item_type': ItemType.objects.all() if request.path != '/item/other/' else ItemType.objects.exclude(id=1),
        'selected_cat1': [int(cat_id) for cat_id in category1_ids],
        'selected_cat2': [int(cat_id) for cat_id in category2_ids],
        'selected_brand': [int(cat_id) for cat_id in category3_ids],
        'selected_type': [int(cat_id) for cat_id in category4_ids],
        'show_note': show_note,
        'show_type': show_type,
        'selected_price': request.GET.getlist('price'),
        'page': page_number,
    }
    return render(request, 'item/list.html', context)

def detail_list_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    sort_by = request.GET.get('sort_by', '-datetime')
    reviews = Review.objects.filter(item=item_id).annotate(likes_count=Count('reviewlike')).order_by('-datetime').prefetch_related(
            Prefetch('reviewreply_set', queryset=ReviewReply.objects.order_by('-datetime')))
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

    context = {
        "item": item,
        "review": page_obj,
        'faqs': faqs,
    } if page_obj else {
        "item": item,
        'message': '리뷰가 없습니다.',
        'faqs': faqs,
    }
    return render(request, 'item/detail.html', context)

@login_required
def add_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    context = {
        "item": item
    }
    if request.method == 'POST':
        item = get_object_or_404(Item, id=item_id)
        user = request.user

        cart_item = Cart.objects.filter(user=user, item=item, status=False).first()
        if cart_item and not cart_item.status:
            cart_item.amount += int(request.POST['current-amount'])
            cart_item.save()
        else:
            Cart.objects.create(user=user, item=item, amount=int(request.POST['current-amount']))

        if int(request.POST['go_cart']) == 1:
            return redirect(request.path)
        elif int(request.POST['go_cart']) == 0:
            return redirect('cart:cart_detail')
    return render(request, 'item/detail.html', context)

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

