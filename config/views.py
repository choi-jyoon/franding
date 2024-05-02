from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from item.models import Item
from django.db.models import Q
from django.core.paginator import Paginator
# Create your views here.

def index(request):
    objects = Item.objects.all().order_by('-id')
    
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
    
def searchItem(request):
    search_word = request.POST.get('search_word', '')
    select_option = request.POST.get('select_option', '')
    objects = None
    
    if select_option == '':
        objects = Item.objects.filter(Q(name__icontains=search_word)| Q(summary__icontains=search_word)|Q(description__icontains=search_word)
                                  |Q(cat1__name__icontains=search_word)|Q(cat2__name__icontains=search_word)|Q(item_type__name__icontains=search_word)
                                  |Q(brand__name__icontains=search_word))
    elif select_option == 'cat1':
        objects = Item.objects.filter(Q(cat1__name__icontains=search_word))
    elif select_option == 'cat2':
        objects = Item.objects.filter(Q(cat2__name__icontains=search_word))
    elif select_option == 'name':
        objects = Item.objects.filter(Q(name__icontains=search_word))
    elif select_option == 'item_type':
        objects = Item.objects.filter(Q(item_type__name__icontains=search_word))
    elif select_option == 'brand':
        objects = Item.objects.filter(Q(brand__name__icontains=search_word))
    elif select_option == 'desc':
        objects = Item.objects.filter(Q(summary__icontains=search_word)|Q(description__icontains=search_word))
        
    paginator = Paginator(objects, 16) # 한 페이지 당 20개의 아이템이 표시되도록 설정합니다.

    page_number = request.GET.get('page', 1) # URL에서 page 넘버를 가져옵니다.
    page_obj = paginator.get_page(page_number) # 해당 페이지의 아이템들만 page_obj에 저장합니다.

    context = {
        'select_option':select_option,
        'search_word':search_word,
        'page_obj': page_obj
    }
    
    return render(request, 'search.html', context)

def about(request):
    return render(request, 'about.html')