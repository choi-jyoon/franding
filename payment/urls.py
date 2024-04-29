from django.urls import path, include
from .views import payment_save, PaymentListView

app_name = 'payment'

urlpatterns = [
    # Add your URL patterns here
    path('', PaymentListView.as_view(), name='payment_list'),
    path('payment_save/', payment_save, name='payment_save'),
]