from django.shortcuts import render, redirect
from .models import Review
from cart.models import OrderCart
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def my_review(request):
    review_list = Review.objects.filter(user = request.user)
    if review_list.exists():
        context ={
            'object_list':review_list
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