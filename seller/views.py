from django.shortcuts import render, redirect, get_object_or_404
from .forms import ItemForm, ReviewReplyForm
from item.models import Item, Brand, ItemType, Size
from review.models import Review, ReviewReply
from cart.models import Order, OrderCart
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
    
    # sort_option 값에 따라 쿼리셋을 정렬합니다.
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
            item.user = request.user  # 현재 로그인한 사용자를 상품의 소유자로 지정합니다.
            
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

# 주문 내역 관리
def seller_orderindex(request):
    sort_option_month = request.GET.get('sort-options-month', 'all')
    sort_option_deliverystatus = request.GET.get('sort-options-deliverystatus', 'all')
    orders = Order.objects.order_by('-datetime')
    
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

def update_delivery_status(request, pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=pk)
        new_status = request.POST.get('delivery_status')
        if new_status is not None:
            order.delivery_info.status = new_status
            order.delivery_info.save()
        return redirect('seller:seller_orderindex')
    
def order_detail(request, pk):
    order = Order.objects.get(pk=pk)
    ordercarts = OrderCart.objects.filter(order_id = pk)
    context={
        'order' : order,
        'ordercarts':ordercarts
    }
    return render(request, 'seller/order_detail.html', context)