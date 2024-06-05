from django.shortcuts import render, redirect, get_object_or_404
from cart.models import OrderCart, Order
from .models import UserAddInfo
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from item.models import ItemLike, Item
from django.contrib import messages



@login_required
def order_index(request):
    orders = Order.objects.filter(ordercart__cart__user=request.user).order_by('-datetime').distinct()
    # Paginator 객체 생성, 한 페이지당 4개의 주문을 보여주도록 설정
    paginator = Paginator(orders, 4)  # 한 페이지당 4개의 주문을 보여줍니다.
    
    # URL의 'page' GET 파라미터로부터 페이지 번호를 가져옵니다. 기본값은 1입니다.
    page_number = request.GET.get('page', 1)
    # 해당 페이지의 주문 객체를 가져옵니다.
    page_obj = paginator.get_page(page_number)
    
    if page_obj:
        context = {
            'orders': page_obj
        }
    else:
        context = {
            'message': '주문 내역이 없습니다.'
        }
    return render(request, 'mypage/order_index.html', context)

def order_detail(request, pk):
    order = Order.objects.get(pk=pk)
    ordercarts = OrderCart.objects.filter(order_id = pk)
    context={
        'order' : order,
        'ordercarts':ordercarts
    }
    return render(request, 'mypage/order_detail.html', context)

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
    user=request.user
    # get
    if request.method=='GET':
        return render(request, 'mypage/add_user_info.html')
    # post
    elif request.method=='POST':
        # 폼에서 전달되는 각 값을 뽑아와서 DB에 저장
        user = request.user
        user_address = request.POST['address']
        user_phone = request.POST['phone']
        
        # 파일 업로드가 있는지 확인
        if 'file' in request.FILES:
            # 이미지 저장 및 url 설정 내용
            fs = FileSystemStorage()
            uploaded_file = request.FILES['file']
            name = fs.save(uploaded_file.name, uploaded_file)
            url = fs.url(name)
        else:
            url = None  # 파일이 없을 경우 None으로 설정
        
        UserAddInfo.objects.create(user=user, address=user_address, phone=user_phone, profile_img = url)

        return redirect('mypage:user_info')
    
@login_required
def update_user_info(request):
    user=request.user
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
        user_info.phone = request.POST['phone']
        user_info.address = request.POST['address']
        user_info.postcode = request.POST['postcode']
        user_info.detailAddress = request.POST['detailAddress']
        user_info.extraAddress = request.POST['extraAddress']
        
        user.last_name = request.POST['last_name']
        user.first_name = request.POST['first_name']
        user.email = request.POST['email']
        
        # 이미지 업데이트 처리
        if 'file' in request.FILES:
            fs = FileSystemStorage()
            uploaded_file = request.FILES['file']
            name = fs.save(uploaded_file.name, uploaded_file)
            url = fs.url(name)
            user_info.profile_img = url
            
        user_info.save()
        user.save()

        return redirect('mypage:user_info')
    
@login_required
def user_delete(request):
    request.user.delete()
    auth_logout(request)
    return redirect('home')

@login_required
def itemlike(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'mypage/wishlist.html', {'wishlist': wishlist})


def add_to_itemlike(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    wishlist = request.session.get('wishlist', [])
    if item_id not in wishlist:
        wishlist.append(item_id)
        request.session['wishlist.html'] = wishlist
        messages.success(request, 'Item successfully added to your wishlist!')
    else:
        messages.info(request, 'Item is already in your wishlist!')
    
    return render(request, 'mypage/wishlist.html')