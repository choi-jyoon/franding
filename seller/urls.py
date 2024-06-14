from django.urls import path
from . import views

app_name='seller'

urlpatterns = [
    # 상품관리
    path('', views.seller_index, name='seller_index'),  # 판매자 페이지
    path('item-create/', views.item_create, name='item_create'),  # 상품 추가 페이지
    path('item-detail/<int:pk>/', views.item_detail, name='item_detail'), # 상품 업데이트 페이지
    path('item-delete/<int:pk>/', views.item_delete, name='item_delete'),  # 상품 삭제 페이지
    path('add-brand/', views.add_brand, name='add_brand'), # 브랜드 추가
    path('add_review_reply/<int:review_id>/', views.add_review_reply, name='add_review_reply'), # 리뷰 대댓글
    # 주문내역관리
    path('seller_orderindex/', views.seller_orderindex, name='seller_orderindex'),
    path('order_detail/<int:pk>/', views.order_detail, name='order_detail'),
    path('update_delivery_status/<str:model_type>/<int:pk>/', views.update_delivery_status, name='update_delivery_status'),
    # 구독관리
    path('subscribe_index/', views.subscribe_index, name='subscribe_index'),
    path('update_keyword/<int:pk>/', views.subscribe_index, name='update_keyword'),
    path('create_keyword/', views.subscribe_index, name='create_keyword'),
    path('delete_keyword/<int:pk>/', views.keyword_delete, name='delete_keyword'),
    path('plot_sub/', views.plot_subscription_trend, name='plot_sub'),
    path('recommend_keyword/', views.recommend_keyword, name='recommend_keyword'),
    # 환불관리
    path('refund_index/', views.refund_index, name='refund_index'),
]
