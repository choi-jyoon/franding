from django.urls import path
from . import views

app_name='subscribe'
urlpatterns = [

    path('', views.membership, name='index'),
    path('pay/', views.payment_process, name='payment'),
    path('<int:pk>/', views.detail, name='subscribe_detail'),
    
]