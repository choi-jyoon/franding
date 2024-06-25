# guide/urls.py

from django.contrib import admin
from django.urls import path
from guide import views

app_name = 'guide'  # 네임스페이스 설정

urlpatterns = [
    path('', views.guide_list, name='guide_list'),
    path('brandstory/', views.brand_philosophy, name='brand_philosophy'),
    path('description/', views.description, name='description'),
    path('pleasant/', views.pleasant, name='pleasant'),
    path('scent/', views.scent, name='scent'),
    path('tale/', views.narrative, name='narrative'),
    path('tip/', views.tip, name='tip'),
]
