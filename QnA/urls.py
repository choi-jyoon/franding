from django.urls import path, re_path
from . import views

app_name = 'QnA'

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:item_id>/', views.question_list, name='question_list'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    # re_path(r'^question/(?P<question_id>[0-9]+)/$', views.question_detail, name='question_detail'),
    path('<int:item_id>/new/', views.question_create, name='question_create'),
]
