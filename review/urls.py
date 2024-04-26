from django.urls import path
from . import views

app_name='review'

urlpatterns = [
    path('', views.my_review, name='review_index'),
    path('create_review/<int:ordercart_id>/', views.create_review, name='create_review'),
]