from django.shortcuts import render, redirect
from cart.models import OrderCart
from .models import UserAddInfo
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

@login_required
def order_index(request):
    user_order_carts = OrderCart.objects.filter(cart__user=request.user)
    if user_order_carts.exists():
        context = {
            'object_list': user_order_carts
        }
    else:
        context = {
            'message': '주문 내역이 없습니다.'
        }
    return render(request, 'mypage/order_index.html', context)

@login_required
def user_info(request):
    try:
        user_info = UserAddInfo.objects.get(user=request.user)
        context={
            'object':user_info
        }
    except:
        context = {
            'message':'회원 정보를 입력해주세요.' 
        }
    return render(request, 'mypage/user_info.html', context)

@login_required
def add_user_info(request):
    # get
    if request.method=='GET':
        return render(request, 'mypage/add_user_info.html')
    # post
    elif request.method=='POST':
        # 폼에서 전달되는 각 값을 뽑아와서 DB에 저장
        user = request.user
        user_address = request.POST['address']
        user_phone = request.POST['phone']
        
        UserAddInfo.objects.create(user=user, address=user_address, phone=user_phone)

        return redirect('mypage:user_info')
    
@login_required
def update_user_info(request):
    # get
    if request.method == 'GET':
        user_info = UserAddInfo.objects.get(user=request.user)
        context = {
            'object': user_info
        }
        return render(request, 'mypage/update_user_info.html', context)
    # post
    elif request.method == 'POST':
        # 폼에서 전달되는 각 값을 뽑아와서 DB에 저장
        user_info = UserAddInfo.objects.get(user=request.user)
        user_info.address = request.POST['address']
        user_info.phone = request.POST['phone']
        user_info.save()

        return redirect('mypage:user_info')
    
@login_required
def user_delete(request):
    request.user.delete()
    auth_logout(request)
    return redirect('home')