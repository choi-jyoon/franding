from django.urls import path
from . import views

app_name='review'

urlpatterns = [
    path('', views.my_review, name='review_index'),
    path('create_review/<int:ordercart_id>/', views.create_review, name='create_review'),
    path('update_review/<int:pk>/', views.update_review, name='update_review'),
    path('review_delete/<int:pk>/', views.review_delete, name='review_delete'),
]