from django.shortcuts import render, redirect
from .models import Review
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def my_review(request):
    objects = Review.objects.filter(user = request.user)
    context ={
        'user' : request.user,
        'review_list':objects
    }
    return render(request, 'review/my_review.html', context)

 
