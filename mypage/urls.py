from django.urls import path
from . import views

app_name='mypage'
urlpatterns = [
    path('', views.order_index, name='order_index'),
    path('userinfo/', views.user_info, name='user_info'),
]