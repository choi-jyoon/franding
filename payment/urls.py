from django.urls import path, include
from .views import payment_list, PaymentDoneView


app_name = 'payment'

urlpatterns = [
    # Add your URL patterns here
    path('', payment_list, name='payment_list'),
    path('payments/', include('payments.urls')),
    path('payment_done/', PaymentDoneView.as_view(), name='payment_done')
]