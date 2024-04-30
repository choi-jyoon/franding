from django.urls import path
from . import views


app_name = 'payment'

urlpatterns = [
    # Add your URL patterns heree
    path('', views.payment_list, name='payment_list'),
    path('paysuccess/', views.paysuccess, name='paysuccess'),
    path('payfail/', views.payfail, name='payfail'),
    path('paycancel/', views.paycancel, name='paycancel'),
]