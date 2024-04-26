from django.urls import path
from . import views

app_name='review'

urlpatterns = [
    path('', views.my_review, name='review_index'),
    # path('create/', views.create_review, name='review_create'),
]