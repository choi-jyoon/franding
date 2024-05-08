from django.shortcuts import render, redirect
from .models import Review
from cart.models import OrderCart
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
# Create your views here.

@login_required
def my_review(request):
    review_list = Review.objects.filter(user = request.user).order_by('-datetime')
    paginator = Paginator(review_list, 4)  # 한 페이지당 4개의 주문을 보여줍니다.
    
    # URL의 'page' GET 파라미터로부터 페이지 번호를 가져옵니다. 기본값은 1입니다.
    page_number = request.GET.get('page', 1)
    # 해당 페이지의 주문 객체를 가져옵니다.
    page_obj = paginator.get_page(page_number)
    
    if page_obj:
        context = {
            'object_list': page_obj
        }
    else:
        context = {
            'message': '작성하신 리뷰가 없습니다.'
        }
    return render(request, 'review/my_review.html', context)


@login_required
def create_review(request, ordercart_id):
    #get
    ordercart = OrderCart.objects.get(pk=ordercart_id)
    if request.method=='GET':
        return render(request, 'review/create_review.html')
    # post
    elif request.method=='POST':
        user = request.user
        item = ordercart.cart.item  # 주문에 대한 상품
        star = int(request.POST['star'])  # 별점
        content = request.POST['content']  # 리뷰 내용

        # 리뷰 객체 생성 및 저장
        Review.objects.create(user=user, item=item, star=star, content=content, orderCart=ordercart)
        
        # 해당 주문 내역의 리뷰 작성 여부 업데이트
        ordercart.is_review = True
        ordercart.save()
                
        return redirect('review:review_index')
    
@login_required
def update_review(request, pk):
    review = Review.objects.get(pk=pk)
    # get
    if request.method == 'GET':
        context = {
            'object': review
        }
        return render(request, 'review/update_review.html', context)
    # post
    elif request.method == 'POST':
        # 폼에서 전달되는 각 값을 뽑아와서 DB에 저장
        review.star = int(request.POST['star']) # 별점
        review.content = request.POST['content']

            
        review.save()

        return redirect('review:review_index')
    
@login_required
def review_delete(request, pk):
    object = Review.objects.get(pk=pk)
    object.delete()
    return redirect('review:review_index')