from django.urls import path
from .views import item_create, item_list, item_detail, item_update, item_delete, seller_page
from . import views

app_name='seller'


urlpatterns = [
    # 판매자 기능을 위한 URL 패턴
    path('', views.seller_page, name='seller_index'),  # 판매자 페이지
    path('item-create/', views.item_create, name='item_create'),  # 상품 추가 페이지
    path('item-list/', views.item_list, name='item_list'),  # 상품 조회 페이지
    path('item-detail', views.item_detail, name='item_detail'), # 상품 상세 페이지
    path('item-update/', views.item_update, name='item_update'), # 상품 업데이트 페이지
    path('item-delete/', views.item_delete, name='item_delete'),  # 상품 삭제 페이지
]
