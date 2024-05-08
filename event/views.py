from django.shortcuts import render
from .forms import PerfumeForm
from .models import Franding
from item.models import Item

# Create your views here.

def index(request):
    return render(request, 'event/index.html')

def recommend_perfume(request):
    if request.method == 'POST':
        form = PerfumeForm(request.POST)
        if form.is_valid():
            intensity = form.cleaned_data['intensity']
            season = form.cleaned_data['season']
            gender = form.cleaned_data['gender']
            age_range = form.cleaned_data['age_range']
            price_range = form.cleaned_data['price_range']
            cat1 = form.cleaned_data['cat1']
            cat2 = form.cleaned_data['cat2']
            
            # 현재 로그인한 사용자와 매칭되는 Franding 인스턴스를 가져오거나, 없으면 새로 생성
            franding, created = Franding.objects.get_or_create(user=request.user)
            
            # Franding 인스턴스 업데이트
            franding.intensity = intensity
            franding.season = season
            franding.gender = gender
            franding.age_range = age_range
            franding.price_range = price_range
            franding.cat1 = cat1
            franding.cat2 = cat2
            franding.save()

            recommendations = Item.objects.filter(cat1__name=franding.cat1, cat2__name=franding.cat2)
            if '1' in price_range:
                recommend = recommendations.filter(price__gte=0, price__lte=70000).first()
            if '2' in price_range:
                recommend = recommendations.filter(price__gte=70000, price__lte=150000).first()
            if '3' in price_range:
                recommend = recommendations.filter(price__gte=150000, price__lte=220000).first()
            if '4' in price_range:
                recommend = recommendations.filter(price__gte=220000).first()
            if '5' in price_range:
                recommend = recommendations.first()
                
            context = {
                'franding':franding,
                'recommend':recommend,
                'recommendations':recommendations,
            }
            return render(request, 'event/results.html', context)
    else:
        form = PerfumeForm()
    return render(request, 'event/recommendation_form.html', {'form': form})