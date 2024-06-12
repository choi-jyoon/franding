# item/urls.py
from django.urls import path, re_path
from . import views

app_name = "item"
urlpatterns = [
    path('', views.list_item, name='item_list'),
    path('brand/', views.list_item, name='brand_list'),
    path('perfume/', views.list_item, name='perfume_list'),
    path('other/', views.list_item, name='other_list'),
    path('<int:item_id>/', views.detail_list_item, name='detail'),
    path('add/<int:item_id>/', views.add_cart, name='add'),
    path('check_like_status/<int:item_id>/', views.check_like_status, name='check_like_status'),  # 좋아요 상태 확인
    path('like_review/', views.like_review, name='like_review'),  # 기존 코드 유지
]
