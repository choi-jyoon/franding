from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chat_response/', views.chat_response, name='chat_response'),
    path('chatbot/', views.chatbot, name='chatbot'),
]
