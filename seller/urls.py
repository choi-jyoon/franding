# seller/urls.py

from django.urls import path
from .views import add_item, view_item, review_list, sales_history, product_search
from . import views

urlpatterns = [
    # 판매자 기능을 위한 URL 패턴
    path('add-item/', add_item, name='add_item'),  # 상품 추가 페이지
    path('view-item/', views.view_item, name='view_item'),  # 상품 조회 페이지
    path('sales-history/', views.sales_history, name='sales_history'),  # 판매 내역 페이지
    path('reviews/', views.review_list, name='review_list'),  # 리뷰 목록 페이지
    path('search/', views.product_search, name='product_search'),  # 상품 검색 페이지
]
