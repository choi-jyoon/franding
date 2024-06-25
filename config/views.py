import json
import uuid
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from requests import Response
from item.models import Item
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import UserAddInfoForm, UserCreateForm, CustomAuthenticationForm, FindUsernameForm
from django.contrib import messages  
from mypage.models import UserAddInfo, EmailToken
from payment.models import Coupon, UserCoupon
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
# Create your views here.

def index(request):
    objects = Item.objects.all().order_by('-id')
    
    context = {
        'item_list' : objects,
    }
    return render(request, 'home.html', context)

def register(request):
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        add_info_form = UserAddInfoForm(request.POST)
        
        if user_form.is_valid() and add_info_form.is_valid():
            # 이메일 중복 검사
            email = user_form.cleaned_data['email']
            if User.objects.filter(email =email).exists():
                user_form.add_error('email', '이미 등록된 이메일입니다.')
                
                context = {
                'user_form': user_form,
                'add_info_form': add_info_form
                }
                return render(request, 'registration/register.html', context)
            
    
            phone = add_info_form.cleaned_data['phone']
            if UserAddInfo.objects.filter(phone = phone).exists():
                add_info_form.add_error('phone', '이미 등록된 휴대폰 번호입니다.')
                context = {
                'user_form': user_form,
                'add_info_form': add_info_form
                }
                return render(request, 'registration/register.html', context)
    
            # User 모델 저장
            user = user_form.save()
            # 이메일 인증 전 : is_active 비활성화
            user.is_active = False
            user.save()

            # UserAddInfo 모델 저장 
            add_info = add_info_form.save(commit=False)
            # UserAddinfo 에 user, 주소 정보 추가
            add_info.user = user
            add_info.postcode = request.POST.get('postcode')  
            add_info.address = request.POST.get('address')   
            add_info.detailAddress = request.POST.get('detailAddress')  
            add_info.extraAddress = request.POST.get('extraAddress')    
            add_info.save()
            
            # 회원가입 쿠폰 지급 
            coupons = Coupon.objects.filter(Q(name__icontains='회원가입'))
            for coupon in coupons : 
                user_coupon = UserCoupon.objects.create(
                    user = user,
                    coupon = coupon
                )
                
            # 사용자 이메일을 세션에 저장
            request.session['user_email'] = user.email

            return redirect('register_done')
        else:
            # 유효성 검사에 실패한 경우
            context = {
                'user_form': user_form,
                'add_info_form': add_info_form
            }
            return render(request, 'registration/register.html', context)
    else:
        user_form = UserCreateForm(initial={'email': request.GET.get('email', '')})
        add_info_form = UserAddInfoForm()
        
        context = {
            'user_form': user_form,
            'add_info_form': add_info_form
        }

        return render(request, 'registration/register.html', context)
    
def send_verification_email(request):
    try:
        #세션에서 사용자 이메일 정보 가져오기
        email = request.session.get('user_email')
        
        # 이메일 중복 확인
        if User.objects.filter(email=email, is_active = True).exists():
            return render(request, 'registration/register_done.html',{'error_message': '이미 등록된 이메일입니다.'})
        
        # 이메일 인증 토큰 생성 및 저장
        expires_at = timezone.now() + timedelta(days=1)
        email_token = EmailToken.objects.create(email=email, expires_at=expires_at)
        
        # 이메일 전송
        email_subject = '회원가입 이메일 인증'
        current_site = get_current_site(request)
        activate_url = reverse('activate_account', args=[email_token.token])
        full_activate_url = f'{current_site.domain}{activate_url}'
        email_message = f'다음 링크를 클릭하여 이메일 인증을 완료하세요: {full_activate_url}'
        send_mail(
            email_subject,
            email_message,
            'from@example.com',
            [email],
            fail_silently=False,
        )

        return render(request, 'registration/register_done.html', {'message': '이메일이 전송되었습니다. 이메일을 확인하고 다음 단계를 진행해주세요.'})
    except (ValueError, TypeError):
        return render(request, 'registration/register_done.html', {'error_message': '잘못된 요청입니다.'})

def activate_account(request, token):
    try:
        email = EmailToken.objects.get(token = token, expires_at__gte=datetime.now())
        user = User.objects.get(email=email.email)
        if not user.is_active:
            user.is_active = True
            user.save()
            return render(request, 'registration/register_done.html', {'success_message': '이메일 인증이 완료되었습니다. 로그인을 진행해주세요.'})
        else:
            # 이미 활성화된 계정인 경우
           return render(request, 'registration/register_done.html', {'error_message': '이미 활성화된 계정입니다.'})
    except User.DoesNotExist:
        return render(request, 'registration/register_done.html', {'error_message': '유효하지 않은 인증 토큰입니다.'})

class UserCreateDoneTV(TemplateView):
    template_name = 'registration/register_done.html'
    

def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # 성공적으로 로그인 후 리다이렉트할 페이지
            return redirect('home')
        else:
            # 폼 유효성 검사에 실패한 경우, 즉 아이디나 비밀번호 오류 등의 이유
            messages.error(request, '로그인 실패. 아이디나 비밀번호를 확인해주세요.')  # 오류 메시지 추가
    else:
        form = CustomAuthenticationForm()

    context = {
        'form': form
    }
    return render(request, 'registration/login.html', context)

def find_username(request):
    if request.method == 'POST':
        form = FindUsernameForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                send_mail(
                    '아이디 찾기 결과',
                    f'회원님의 아이디는 {user.username}입니다.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, '아이디가 이메일로 전송되었습니다.')
                return redirect('login')
            except User.DoesNotExist:
                form.add_error('email', '해당 이메일로 등록된 사용자가 없습니다.')
    else:
        form = FindUsernameForm()

    return render(request, 'registration/find_username.html', {'form': form})


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    
    def form_valid(self, form):
        return super().form_valid(form)

    
def searchItem(request):
    search_word = request.GET.get('search_word', '') or request.POST.get('search_word', '')
    select_option = request.GET.get('select_option', '') or request.POST.get('select_option', '')
    objects = Item.objects.all()

    if search_word or select_option:
        if select_option == '' or select_option == '분류':
            objects = Item.objects.filter(Q(name__icontains=search_word) | Q(summary__icontains=search_word) | Q(description__icontains=search_word)
                                          | Q(cat1__name__icontains=search_word) | Q(cat2__name__icontains=search_word) | Q(item_type__name__icontains=search_word)
                                          | Q(brand__name__icontains=search_word))
        elif select_option == 'cat1':
            objects = Item.objects.filter(Q(cat1__name__icontains=search_word))
        elif select_option == 'cat2':
            objects = Item.objects.filter(Q(cat2__name__icontains=search_word))
        elif select_option == 'name':
            objects = Item.objects.filter(Q(name__icontains=search_word))
        elif select_option == 'item_type':
            objects = Item.objects.filter(Q(item_type__name__icontains=search_word))
        elif select_option == 'brand':
            objects = Item.objects.filter(Q(brand__name__icontains=search_word))
        elif select_option == 'desc':
            objects = Item.objects.filter(Q(summary__icontains=search_word) | Q(description__icontains=search_word))
            
    paginator = Paginator(objects, 16) 

    page_number = request.GET.get('page', 1) 
    page_obj = paginator.get_page(page_number) 

    context = {
        'select_option':select_option,
        'search_word':search_word,
        'page_obj': page_obj
    }
    
    return render(request, 'search.html', context)

def about(request):
    return render(request, 'about.html')
