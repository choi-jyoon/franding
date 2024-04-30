
from django.urls import path, re_path
from . import views
app_name = "item"
urlpatterns = [
path('', views.list_item, name='item_list'),
path('<int:item_id>/',views.detail_list_item,name='detail'),
]
