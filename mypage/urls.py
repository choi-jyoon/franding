from django.urls import path
from . import views

app_name='mypage'
urlpatterns = [
    path('', views.order_index, name='order_index'),
]