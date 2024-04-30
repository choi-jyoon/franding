from django.shortcuts import render
from django.views.generic import TemplateView
from cart.models import Cart




# Create your views here.
def payment_list(request, total_price=0):
    template_name = 'payment/payment_info.html'
    item_list = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id')
    

    for c in item_list:
        total_price += (c.item.price * c.amount)
    
    context = {
            'item_list': item_list,
            'total_price': total_price
    }
    
    return render(request, template_name, context)
        

class PaymentDoneView(TemplateView):
    template_name = 'payment/payment_done.html'
    
