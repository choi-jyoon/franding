from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ItemForm
from item.models import Item, Brand, ItemType, Size
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.core.files.storage import FileSystemStorage




@login_required
def seller_page(request):
    items = Item.objects.all().order_by('-created_at')
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    if page_obj:
        context = {
            'items': page_obj
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
            return redirect('seller:item_list')  # 상품 목록 페이지로 리디렉션합니다. -> item_list 오류 : item:item_list 로 url 네임 명시
        
    else:
        form = ItemForm()
    return render(request, 'seller/item_form.html', {'form': form})


@login_required
def item_list(request):
    items = Item.objects.all()
    return render(request, 'seller/item_list.html', {'items': items})

@login_required
def item_detail(request, product_name, size):
    # DB에서 제품명과 사이즈에 해당하는 제품을 가져옵니다.
    try:
        item = Item.objects.get(name=product_name, size=size)
    except Item.DoesNotExist:
        # 제품이 존재하지 않을 경우 404 에러를 반환합니다.
        raise Http404("제품을 찾을 수 없습니다.")

    # 제품 상세 페이지를 렌더링합니다.
    return render(request, 'seller/item_detail.html', {'item': item})


@login_required
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
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
            return redirect('seller:item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'seller/item_form.html', {'form': form})\
        
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
        return redirect('seller:item_list')
    return render(request, 'seller/item_confirm_delete.html', {'item': item})


class ItemListView(ListView):
    model = Item
    template_name = 'seller/item_list.html'  # 'seller' 앱 내의 템플릿 경로로 수정
    paginate_by = 10

    def get_queryset(self):
        return Item.objects.all().order_by('-created_at')