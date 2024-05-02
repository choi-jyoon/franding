from django.shortcuts import render, redirect
from django.views.generic import ListView,DetailView
from django.views.generic import FormView

from django.db.models import Q
from .models import *
from cart.models import Cart
# Create your views here.

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


#category 정리
#100번대->cat1
#200번대->cat2
#250번대->detail_cat2
#300번대->brand
#400번대->item_type

def list_item(request):
    items = Item.objects.all()
    
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
    if request.path == '/item/perfume/':
        items = items.filter(item_type__id__in= ['1'])
    elif request.path == '/item/other/':
        items = items.exclude(item_type__id__in=['1'])
        if category4_ids:
            items = items.filter(item_type__id__in=category4_ids)
    else:
        if category4_ids:
            items = items.filter(item_type__id__in=category4_ids)
    
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
        'show_cat':False
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
        }
    return render(request, 'item/list.html', context)


def detail_list_item(request,item_id):
    item=Item.objects.get(id=item_id)
    context={
        "item":item
    }
    if request.method == 'POST':
        item = Item.objects.get(id=item_id)
        user = request.user

        # 장바구니에 동일한 상품이 있는지 확인
        cart_item = Cart.objects.filter(user=user, item=item).first()
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
        return redirect(request.path)
    else:
        return render(request,'item/detail.html',context)    
    

    
