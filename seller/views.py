from django.shortcuts import render, redirect
from .models import Item
from .forms import ItemForm
from .models import Review
from .models import Product
from .models import Order

def add_item(request):
    # POST 요청을 처리하여 새 Item 객체를 생성하고 저장합니다.
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():  # 폼의 유효성을 검증합니다.
            form.save()  # 데이터가 유효하면 폼 데이터를 데이터베이스에 저장합니다.
            return redirect('seller_dashboard')  # 저장 후 판매자 대시보드로 리디렉션합니다.
    else:
        form = ItemForm()  # GET 요청인 경우 빈 폼을 생성합니다.
    return render(request, 'seller/add_item.html', {'form': form})

def view_item(request):
    # 모든 제품을 검색하여 view_item.html 템플릿으로 렌더링합니다.
    products = Product.objects.all()
    return render(request, 'seller/view_item.html', {'products': products})

def review_list(request):
    # 모든 리뷰를 검색하여 review_list.html 템플릿으로 렌더링합니다.
    reviews = Review.objects.all()
    return render(request, 'seller/review_list.html', {'reviews': reviews})

def product_search(request):
    # 쿼리 매개변수를 기반으로 제품 검색을 처리합니다.
    query = request.GET.get('q')
    if query:
        products = Product.search(query)  # 쿼리에 기반하여 제품을 검색합니다.
    else:
        products = None
    return render(request, 'seller/product_search.html', {'products': products, 'query': query})

def sales_history(request):
    # 모든 주문을 검색하여 sales_history.html 템플릿으로 렌더링합니다.
    orders = Order.objects.all()
    return render(request, 'seller/sales_history.html', {'orders': orders})
