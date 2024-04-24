from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from item.models import Item
# Create your views here.

def index(request):
    objects = Item.objects.all()[:4]
    context = {
        'item_list' : objects
    }
    return render(request, 'home.html', context)

class UserCreateView(CreateView):
    template_name='registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register_done')
    
class UserCreateDoneTV(TemplateView):
    template_name = 'registration/register_done.html'
    
