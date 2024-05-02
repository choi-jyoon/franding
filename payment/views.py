from django.shortcuts import render
from django.views.generic import TemplateView
from cart.models import Cart



# Create your views here.
def payment_list(request, total_price=0):
    template_name = 'payment/payment_info.html'
    # item_list = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')

    if request.method == 'GET':
        checkbox_item = request.GET.getlist('checkbox')
        check_item_list = []
    
    for check in checkbox_item:   
        try:
            # 만약 check가 숫자가 아니라면 ValueError가 발생
            check = int(check)   
        except ValueError: 
            print('선택된 상품이 없습니다.') 
            
        check_item = Cart.objects.get(user=request.user, item=check, status=False) 
        check_item_list.append(check_item)
        total_price += (check_item.item.price * check_item.amount)
        
        
    
    context = {
            'item_list': check_item_list,
            'total_price': total_price
    }
    
    return render(request, template_name, context)
        

class PaymentDoneView(TemplateView):
    template_name = 'payment/payment_done.html'
    
