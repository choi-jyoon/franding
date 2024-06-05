from django.urls import path
from . import views

app_name='seller'

urlpatterns = [
    path('', views.seller_index, name='seller_index'),  # 판매자 페이지
    path('item-create/', views.item_create, name='item_create'),  # 상품 추가 페이지
    # path('item-list/', ItemListView.as_view(), name='item_list'),  # 상품 조회 페이지
    path('item-detail/<int:pk>/', views.item_detail, name='item_detail'), # 상품 업데이트 페이지
    path('item-delete/<int:pk>/', views.item_delete, name='item_delete'),  # 상품 삭제 페이지
    path('add-brand/', views.add_brand, name='add_brand'),
]
