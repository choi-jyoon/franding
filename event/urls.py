from django.urls import path
from . import views

app_name='event'
urlpatterns = [
    path('', views.index, name='index'),
    path('recommend-perfume/', views.recommend_perfume, name='recommend-perfume'),
]