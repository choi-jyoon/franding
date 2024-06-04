"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from cart import views
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

app_name = 'cart'

router = DefaultRouter()
router.register(r'items', CartViewSet)

urlpatterns = [           
    path('detail/', views.cart_detail, name='cart_detail'),    
    path('accept_ajax/', views.accept_ajax, name='ajax'),    
    path('cart_delete/', views.cart_delete, name='cart_delete'),
    path('', include(router.urls)),
]
