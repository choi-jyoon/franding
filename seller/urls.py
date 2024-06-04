from django.urls import path
from .views import item_create, item_list, item_detail, item_update, item_delete, seller_page
from . import views
from .views import ItemListView

app_name='seller'

urlpatterns = [
    path('', views.seller_page, name='seller_index'),  # 판매자 페이지
    path('item-create/', views.item_create, name='item_create'),  # 상품 추가 페이지
    path('item-list/', ItemListView.as_view(), name='item_list'),  # 상품 조회 페이지
    path('item-update/<int:pk>/', views.item_update, name='item_update'), # 상품 업데이트 페이지
    path('item-delete/<int:pk>/', views.item_delete, name='item_delete'),  # 상품 삭제 페이지
    path('add-brand/', views.add_brand, name='add_brand'),
]
