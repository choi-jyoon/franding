from django.shortcuts import render
from django.views.generic import ListView,DetailView
from django.views.generic import FormView

from django.db.models import Q
from .models import *
# Create your views here.

def list_item(request):
    model = Item.objects.all()
    context={
        "item":model
    }
    return render(request,'item/list.html',context)
    pass
def cat_list_item(request,cat_id):
    if int(cat_id)>=100 and int(cat_id)<200:
        cat_id = cat_id-100
        cat = Category1.objects.get(id=cat_id)
        #아이템 모델에서 카테고리 1 값이 cat과 동일한 데이터를 찾아서 반환
       
        context={
        "key":Item.objects.filter(cat1 = cat)
        }
         #리퀘스트, 템플릿주소, 콘텍스트 를 반환
        return render(request,'item/cat_list.html',context)
    elif int(cat_id)>=200 and int(cat_id)<300:
        cat_id = cat_id-200
        cat= Category2.objects.get(id=cat_id)
        context={
        "key":Item.objects.filter(cat2 = cat)
        }
      
        return render(request,'item/cat_list.html',context)
    elif int(cat_id)>=300 and int(cat_id)<400:
        cat_id = cat_id-300
        cat = Brand.objects.get(id=cat_id)
        context={
        "key":Item.objects.filter(brand = cat)
        }

        return render(request,'item/cat_list.html',context)
    elif int(cat_id)>=400 and int(cat_id)<500:
        cat_id = cat_id-400
        cat = ItemType.objects.get(id=cat_id)
        context={
        "key":Item.objects.filter(item_type = cat)
        }
      
        return render(request,'item/cat_list.html',context)

