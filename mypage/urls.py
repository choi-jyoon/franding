from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    # 주문내역
    path('', views.order_index, name='order_index'),
    path('order_detail/<int:pk>', views.order_detail, name='order_detail'),
    path('order_confirm/<int:pk>', views.order_confirm, name='order_confirm'),
    path('order_refund/<int:pk>', views.order_refund, name='order_refund'),
    path('refund_confirm/<int:pk>', views.refund_confirm, name='refund_confirm'),
    
    
    # 회원정보
    path('userinfo/', views.user_info, name='user_info'), # 회원정보
    path('add_userinfo/', views.add_user_info, name='add_user_info'), # 등록
    path('update_userinfo/', views.update_user_info, name='update_user_info'), # 수정
    path('user_delete/', views.user_delete, name='user_delete'), # 탈퇴
    
    # 내 쿠폰
    path('coupon/', views.user_coupon, name='user_coupon'), 
    
]
