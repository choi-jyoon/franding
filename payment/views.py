from django.shortcuts import render
from django.views.generic import TemplateView
# from .models import Cart


# Create your views here.
class PaymentListView(TemplateView):
    template_name = 'payment/payment_info.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['item_list'] = Order.objects.all()
        return context
    

def payment_save(request):
        
    # 결제 정보를 입력하는 템플릿 만들기
    # 템플릿에서 결제 정보를 가져오기
    # 결제 정보를 데이터베이스에 저장하기
    # 결제 정보 저장 후 결제 완료 페이지로 이동하기
    # 결제 완료 페이지에서 결제 정보 보여주기, 결제 취소하기, 배송 정보 확인하기, Q&A 게시판으로 이동하기
    if request.method == 'POST':
        pass

# Create your views here.
