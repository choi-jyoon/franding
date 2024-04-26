from django.shortcuts import render, redirect
from .models import Review
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