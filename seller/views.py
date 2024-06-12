from django.shortcuts import render, redirect, get_object_or_404
from .forms import ItemForm, ReviewReplyForm, KeywordForm
from item.models import Item, Brand, ItemType, Size
from review.models import Review, ReviewReply
from cart.models import Order, OrderCart
from subscribe.models import Keyword, Subscribe
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.files.storage import FileSystemStorage
from django.db.models import Avg, Value, IntegerField, Count, Q
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear



# 상품관리(등록,수정,삭제 등등)
@login_required
def seller_index(request):
    sort_option = request.GET.get('sort-options', 'newest')
    
    # sort_option 값에 따라 쿼리셋을 정렬
    if sort_option == 'newest':
        items = Item.objects.order_by('-created_at') # 최신순
    elif sort_option == 'popularity':
        items = Item.objects.annotate(order_count=Count('cart', filter=Q(cart__status=True))).order_by('-order_count') # 인기순(주문 많은 순)
    elif sort_option == 'starHighToLow':
        # 평점 높은 순(평점이 없는경우는 0으로 처리)
        items = Item.objects.annotate(average_rating=Coalesce(Avg('review__star'), Value(0), output_field=IntegerField())).order_by('-average_rating')
    elif sort_option == 'starLowToHigh':
        items = Item.objects.annotate(average_rating=Avg('review__star')).order_by('average_rating') # 평점 낮은 순
    elif sort_option == 'inventoryLowToHigh':
        items = Item.objects.order_by('inventory') # 재고 낮은 순
    elif sort_option == 'inventoryHighToLow':
        items = Item.objects.order_by('-inventory') # 재고 높은 순
        
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    if page_obj:
        context = {
            'items': page_obj,
            'sort_option': sort_option
        }
    return render(request, 'seller/seller_index.html', context)



@login_required
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user  # 현재 로그인한 사용자를 상품의 소유자로 지정
            
            # 파일 업로드가 있는지 확인
            if 'image' in request.FILES:
                # 이미지 저장 및 url 설정 내용
                fs = FileSystemStorage()
                uploaded_file = request.FILES['image']
                name = fs.save(uploaded_file.name, uploaded_file)
                url = fs.url(name)
                item.image = url

            item.save()
            return redirect('seller:seller_index')  # 상품 목록 페이지로 리디렉션합니다. -> item_list 오류 : item:item_list 로 url 네임 명시
        
    else:
        form = ItemForm()
    return render(request, 'seller/item_form.html', {'form': form})


@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    reviews = Review.objects.filter(item=item).order_by('-datetime')
    average = reviews.aggregate(Avg('star'))['star__avg']
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        
        if form.is_valid():
            if 'image' in request.FILES:
                # 이미지 저장 및 url 설정 내용
                fs = FileSystemStorage()
                uploaded_file = request.FILES['image']
                name = fs.save(uploaded_file.name, uploaded_file)
                url = fs.url(name)
                item.image = url

            form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = ItemForm(instance=item)
        
    context={
        'form': form,
        'item': item,
        'reviews': reviews,
        'average': average,
    }
    return render(request, 'seller/item_detail.html', context)
        
def add_brand(request):
    if request.method == 'POST':
        name = request.POST.get('field-name')
        field = request.POST.get('field-type')
        if field == 'brand':
            Brand.objects.create(name=name)
        elif field == 'item_type':
            ItemType.objects.create(name=name)
        elif field == 'size':
            ml=int(name)
            Size.objects.create(ml=ml)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('seller:seller_index')
    return render(request, 'seller/item_confirm_delete.html', {'item': item})

@login_required
def add_review_reply(request, review_id):
    review = Review.objects.get(id=review_id)
    if request.method == "POST":
        form = ReviewReplyForm(request.POST)
        if form.is_valid():
            ReviewReply.objects.create(
                review=review,
                user=request.user,
                comment=form.cleaned_data['comment']
            )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# 주문 내역 관리(주문내역, 주문상세, 배송상태 설정 등)
@login_required
def seller_orderindex(request):
    sort_option_month = request.GET.get('sort-options-month', 'all')
    sort_option_deliverystatus = request.GET.get('sort-options-deliverystatus', 'all')
    orders = Order.objects.order_by('-datetime')
    # 필터링 기준
    if sort_option_month != 'all' and sort_option_deliverystatus != 'all':
        year, month = map(int, sort_option_month.split('-'))
        orders = orders.filter(datetime__year=year, datetime__month=month, delivery_info__status=int(sort_option_deliverystatus))
    elif sort_option_month != 'all':
        year, month = map(int, sort_option_month.split('-'))
        orders = orders.filter(datetime__year=year, datetime__month=month)
    elif sort_option_deliverystatus != 'all':
        orders = orders.filter(delivery_info__status=int(sort_option_deliverystatus))
    else:
        orders = Order.objects.order_by('-datetime')
        
    months_queryset = Order.objects.annotate(year=ExtractYear('datetime'),month=ExtractMonth('datetime')).values('year', 'month').distinct().order_by('-year', '-month')
    months = [f"{entry['year']}-{entry['month']:02d}" for entry in months_queryset]
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders':page_obj,
        'months':months,
        'sort_option_month': sort_option_month,
        'sort_option_deliverystatus': sort_option_deliverystatus,
    }
    return render(request, 'seller/order_index.html', context)
    
@login_required
def update_delivery_status(request, model_type, pk):
    if request.method == 'POST':
        if model_type == 'order':
            order = get_object_or_404(Order, id=pk)
            new_status = request.POST.get('delivery_status')
            if new_status is not None:
                order.delivery_info.status = new_status
                order.delivery_info.save()
            return redirect('seller:seller_orderindex')
        elif model_type == 'subscribe':
            subscribe = get_object_or_404(Subscribe, id=pk)
            new_status = request.POST.get('delivery_status')
            if new_status is not None:
                subscribe.delivery.status = new_status
                subscribe.delivery.save()
            return redirect('seller:subscribe_index')


@login_required    
def order_detail(request, pk):
    order = Order.objects.get(pk=pk)
    ordercarts = OrderCart.objects.filter(order_id = pk)
    context={
        'order' : order,
        'ordercarts':ordercarts
    }
    return render(request, 'seller/order_detail.html', context)

# 구독관리
@login_required
def subscribe_index(request, pk=None):
    
    # 구독 키워드 관리
    sort_option_month = request.GET.get('sort-options-month', 'all')
    keywords = Keyword.objects.order_by('-month')
    # 필터링 기준 - 월 기준
    if sort_option_month != 'all':
        created_year, created_month = map(int, sort_option_month.split('-'))
        keywords = keywords.filter(month__year=created_year, month__month=created_month)
        
    keyword_months_queryset = Keyword.objects.annotate(created_year=ExtractYear('month'),created_month=ExtractMonth('month')).values('created_year', 'created_month').distinct().order_by('-created_year', '-created_month')
    keyword_months = [f"{entry['created_year']}-{entry['created_month']:02d}" for entry in keyword_months_queryset]
    
    if pk:
        keyword = get_object_or_404(Keyword, pk=pk)
    else:
        keyword = None
    
    if request.method == 'POST':
        form = KeywordForm(request.POST, instance=keyword)
        if form.is_valid():
            form.save()
        return redirect('seller:subscribe_index')
    else:
        form = KeywordForm(instance=keyword)
        
    # 구독 고객 리스트 관리
    sub_option_month = request.GET.get('sub-options-month', 'all')
    sub_option_deliverystatus = request.GET.get('sub-options-deliverystatus', 'all')
    subscribes = Subscribe.objects.order_by('-datetime')

    # 필터링 기준(월,배송상태)
    if sub_option_month != 'all' and sub_option_deliverystatus != 'all':
        year, month = map(int, sub_option_month.split('-'))
        subscribes = subscribes.filter(datetime__year=year, datetime__month=month, delivery__status=int(sub_option_deliverystatus))
    elif sub_option_month != 'all':
        year, month = map(int, sub_option_month.split('-'))
        subscribes = subscribes.filter(datetime__year=year, datetime__month=month)
    elif sub_option_deliverystatus != 'all':
        subscribes = subscribes.filter(delivery__status=int(sub_option_deliverystatus))
        
    sub_months_queryset = Subscribe.objects.annotate(year=ExtractYear('datetime'),month=ExtractMonth('datetime')).values('year', 'month').distinct().order_by('-year', '-month')
    sub_months = [f"{entry['year']}-{entry['month']:02d}" for entry in sub_months_queryset]
    
    paginator = Paginator(subscribes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context={
        'keywords':keywords,
        'keyword_months':keyword_months,
        'sort_option_month':sort_option_month,
        'form':form,
        'subscribes':page_obj,
        'sub_months':sub_months,
        'sub_option_month':sub_option_month,
        'sub_option_deliverystatus':sub_option_deliverystatus,
    }
    return render(request, 'seller/subscribe_index.html', context)