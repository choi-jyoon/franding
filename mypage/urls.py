from django.urls import path
from . import views

app_name='mypage'
urlpatterns = [
    path('', views.order_index, name='order_index'),
    path('userinfo/', views.user_info, name='user_info'),
    path('add_userinfo/', views.add_user_info, name='add_user_info'),
    path('update_userinfo/', views.update_user_info, name='update_user_info'),
]