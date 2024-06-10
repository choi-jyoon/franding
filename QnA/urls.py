from django.urls import path, re_path
from . import views

app_name = 'QnA'

urlpatterns = [
    path('', views.home, name='home'),
    path('answer/<int:question_id>/', views.answer_detail, name='answer_detail'),
    path('seller_questions/', views.seller_questions, name='seller_questions'),
    path('answer_question/<int:question_id>/', views.answer_question, name='answer_question'),
    path('<int:item_id>/new/', views.question_create, name='question_create'),
]
