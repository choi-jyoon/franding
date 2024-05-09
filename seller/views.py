from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ItemForm
from item.models import Item
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView




@login_required
def seller_page(request):
    return render(request, 'seller/seller_index.html')


@login_required
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user  # 현재 로그인한 사용자를 상품의 소유자로 지정합니다.
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
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('seller:item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'seller/item_form.html', {'form': form})


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



# 5페이지 이동 및 검색 보류 뷰
# class ItemListView(ListView):
#     model = Item
#     template_name = 'app/item_list.html'
#     context_object_name = 'item_list'
#     paginate_by = 4

#     def get_queryset(self):
#         query = self.request.GET.get('q', '')  # 검색어 받기
#         object_list = Item.objects.filter(name__icontains=query)  # 이름에 검색어 포함된 상품만 검색
#         return object_list

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         query = self.request.GET.get('q', '')  # 검색어 받기
#         paginator = context['paginator']
#         page_numbers_range = 5  # 페이지 번호 범위 설정
#         max_index = len(paginator.page_range)
#         page = self.request.GET.get('page')
#         current_page = int(page) if page else 1

#         start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
#         end_index = start_index + page_numbers_range
#         if end_index >= max_index:
#             end_index = max_index

#         page_range = paginator.page_range[start_index:end_index]
#         context['page_range'] = page_range
#         context['query'] = query  # 검색어 유지
#         return context