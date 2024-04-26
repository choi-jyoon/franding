from django.shortcuts import render
from django.views.generic import ListView,DetailView
from django.views.generic import FormView

from django.db.models import Q
from .models import *
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
    
    if category1_ids:
        items = items.filter(cat1__id__in=category1_ids)
    if category2_ids:
        items = items.filter(cat2__id__in=category2_ids)
    
    paginator = Paginator(items, 4)  # 한 페이지에 20개씩 표시
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
        'selected_cat1':[int(cat_id) for cat_id in category1_ids],
        'selected_cat2':[int(cat_id) for cat_id in category2_ids],
    }
    return render(request, 'item/list.html', context)

def detail_list_item(request,item_id):
    model=Item.objects.get(id=item_id)
    context={
        "item":model
    }
    return render(request,'item/detail.html',context)
