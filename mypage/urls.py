from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    # 주문내역
    path('', views.order_index, name='order_index'),
    path('order_detail/<int:pk>', views.order_detail, name='order_detail'),
    
    # 회원정보
    path('userinfo/', views.user_info, name='user_info'), # 회원정보
    path('add_userinfo/', views.add_user_info, name='add_user_info'), # 등록
    path('update_userinfo/', views.update_user_info, name='update_user_info'), # 수정
    path('user_delete/', views.user_delete, name='user_delete'), # 탈퇴

    # 찜 목록
    path('item_likes/', views.item_like_page, name='item_like_page'),
    # path('toggle_like/<int:item_id>/', views.toggle_like, name='toggle_like'),
]
