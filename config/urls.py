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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
# from cart.views import

urlpatterns = [
    path('', views.index, name='home'),
    path('badge_count/', views.badge_count, name='badge_count'),
    path('admin/', admin.site.urls),
    path("item/", include("item.urls")),
    path('mypage/', include('mypage.urls')),
    path('cart/', include('cart.urls')),
    path('review/', include('review.urls')),
    path('event/', include('event.urls')),
    path('subscribe/', include('subscribe.urls')),
    path('about/',views.about, name='about' ),
    path('search/', views.searchItem, name='search' ),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('accounts/', include('allauth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('accounts/register/done/', views.UserCreateDoneTV.as_view(), name='register_done'),
    path('seller/', include('seller.urls')),
    path('payment/', include('payment.urls')),
    path('QnA/', include('QnA.urls')),    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
