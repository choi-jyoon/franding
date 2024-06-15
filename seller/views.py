from django.shortcuts import render, redirect, get_object_or_404
from .forms import ItemForm, ReviewReplyForm, KeywordForm
from item.models import Item, Brand, ItemType, Size
from review.models import Review, ReviewReply
from cart.models import Order, OrderCart
from subscribe.models import Keyword, Subscribe, SubscribeKeyword
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.files.storage import FileSystemStorage
from django.db.models import Avg, Value, IntegerField, Count, Q
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear
import plotly.express as px
import pandas as pd
from django.views.decorators.http import require_GET
from django.conf import settings
from langchain_community.utilities import SQLDatabase
from django.http import JsonResponse
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from operator import itemgetter
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os

from dotenv import load_dotenv
# 상품관리(등록,수정,삭제 등등)
@login_required
def seller_index(request):
    sort_option = request.GET.get('sort-options', 'newest')
    # 기본 쿼리셋
    items = Item.objects.select_related('brand').only('brand__name','inventory','image','name','price').order_by('-created_at')

    # sort_option 값에 따라 쿼리셋을 정렬
    if sort_option == 'newest':
        items = items.order_by('-created_at')
    elif sort_option == 'popularity':
        items = items.annotate(order_count=Count('cart', filter=Q(cart__status=True))).order_by('-order_count')
    elif sort_option == 'starHighToLow':
        items = items.annotate(average_rating=Coalesce(Avg('review__star'), Value(0), output_field=IntegerField())).order_by('-average_rating')
    elif sort_option == 'starLowToHigh':
        items = items.annotate(average_rating=Coalesce(Avg('review__star'), Value(0), output_field=IntegerField())).order_by('average_rating')
    elif sort_option == 'inventoryLowToHigh':
        items = items.order_by('inventory')
    elif sort_option == 'inventoryHighToLow':
        items = items.order_by('-inventory')

    # related_name을 사용하여 prefetch_related
    items = items.prefetch_related('review_set')
        
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    if page_obj:
        context = {
            'items': page_obj,
            'sort_option': sort_option
        }
    return render(request, 'seller/seller_index.html', context)


@login_required
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user  # 현재 로그인한 사용자를 상품의 소유자로 지정
            
            # 파일 업로드가 있는지 확인
            if 'image' in request.FILES:
                # 이미지 저장 및 url 설정 내용
                fs = FileSystemStorage()
                uploaded_file = request.FILES['image']
                name = fs.save(uploaded_file.name, uploaded_file)
                url = fs.url(name)
                item.image = url

            item.save()
            return redirect('seller:seller_index')  # 상품 목록 페이지로 리디렉션합니다. -> item_list 오류 : item:item_list 로 url 네임 명시
        
    else:
        form = ItemForm()
    return render(request, 'seller/item_form.html', {'form': form})


@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    reviews = Review.objects.filter(item=item).select_related('user').prefetch_related('reviewreply_set').order_by('-datetime')
    average = reviews.aggregate(Avg('star'))['star__avg']
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        
        if form.is_valid():
            if 'image' in request.FILES:
                # 이미지 저장 및 url 설정 내용
                fs = FileSystemStorage()
                uploaded_file = request.FILES['image']
                name = fs.save(uploaded_file.name, uploaded_file)
                url = fs.url(name)
                item.image = url

            form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = ItemForm(instance=item)
        
    context={
        'form': form,
        'item': item,
        'reviews': reviews,
        'average': average,
    }
    return render(request, 'seller/item_detail.html', context)
        
def add_brand(request):
    if request.method == 'POST':
        name = request.POST.get('field-name')
        field = request.POST.get('field-type')
        if field == 'brand':
            Brand.objects.create(name=name)
        elif field == 'item_type':
            ItemType.objects.create(name=name)
        elif field == 'size':
            ml=int(name)
            Size.objects.create(ml=ml)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('seller:seller_index')
    return render(request, 'seller/item_confirm_delete.html', {'item': item})

@login_required
def add_review_reply(request, review_id):
    review = Review.objects.get(id=review_id)
    if request.method == "POST":
        form = ReviewReplyForm(request.POST)
        if form.is_valid():
            ReviewReply.objects.create(
                review=review,
                user=request.user,
                comment=form.cleaned_data['comment']
            )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# 주문 내역 관리(주문내역, 주문상세, 배송상태 설정 등)
@login_required
def seller_orderindex(request):
    sort_option_month = request.GET.get('sort-options-month', 'all')
    sort_option_deliverystatus = request.GET.get('sort-options-deliverystatus', 'all')
    orders = Order.objects.select_related('delivery_info').order_by('-datetime')
    # 필터링 기준
    if sort_option_month != 'all':
        year, month = map(int, sort_option_month.split('-'))
        orders = orders.filter(datetime__year=year, datetime__month=month)
    if sort_option_deliverystatus != 'all':
        orders = orders.filter(delivery_info__status=int(sort_option_deliverystatus))
        
    months_queryset = Order.objects.annotate(year=ExtractYear('datetime'),month=ExtractMonth('datetime')).values('year', 'month').distinct().order_by('-year', '-month')
    months = [f"{entry['year']}-{entry['month']:02d}" for entry in months_queryset]
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders':page_obj,
        'months':months,
        'sort_option_month': sort_option_month,
        'sort_option_deliverystatus': sort_option_deliverystatus,
    }
    return render(request, 'seller/order_index.html', context)
    
@login_required
def update_delivery_status(request, model_type, pk):
    if request.method == 'POST':
        if model_type == 'order':
            order = get_object_or_404(Order, id=pk)
            new_status = request.POST.get('delivery_status')
            if new_status is not None:
                order.delivery_info.status = new_status
                order.delivery_info.save()
            return redirect('seller:seller_orderindex')
        elif model_type == 'subscribe':
            subscribe = get_object_or_404(Subscribe, id=pk)
            new_status = request.POST.get('delivery_status')
            if new_status is not None:
                subscribe.delivery.status = new_status
                subscribe.delivery.save()
            return redirect('seller:subscribe_index')


@login_required    
def order_detail(request, pk):
    order = Order.objects.get(pk=pk)
    ordercarts = OrderCart.objects.filter(order_id = pk)
    context={
        'order' : order,
        'ordercarts':ordercarts
    }
    return render(request, 'seller/order_detail.html', context)

# 구독관리
@login_required
def subscribe_index(request, pk=None):
    # 구독 키워드 관리
    sort_option_month = request.GET.get('sort-options-month', 'all')
    keywords = Keyword.objects.select_related('category1', 'category2').only('id', 'word', 'month','category1__name','category2__name').order_by('-month')
    # 필터링 기준 - 월 기준
    if sort_option_month != 'all':
        created_year, created_month = map(int, sort_option_month.split('-'))
        keywords = keywords.filter(month__year=created_year, month__month=created_month)
        
    keyword_months_queryset = Keyword.objects.annotate(created_year=ExtractYear('month'),created_month=ExtractMonth('month')).values('created_year', 'created_month').distinct().order_by('-created_year', '-created_month')
    keyword_months = [f"{entry['created_year']}-{entry['created_month']:02d}" for entry in keyword_months_queryset]
    
    keyword = get_object_or_404(Keyword, pk=pk) if pk else None
    
    if request.method == 'POST':
        form = KeywordForm(request.POST, instance=keyword)
        if form.is_valid():
            form.save()
        return redirect('seller:subscribe_index')
    else:
        form = KeywordForm(instance=keyword)
        
    # 구독 고객 리스트 관리
    sub_option_month = request.GET.get('sub-options-month', 'all')
    sub_option_deliverystatus = request.GET.get('sub-options-deliverystatus', 'all')
    # subscribes = Subscribe.objects.select_related('delivery','user').order_by('-datetime')
    subscribes = Subscribe.objects.select_related('delivery', 'user', 'item').only('user__username', 'datetime', 'item__name', 'delivery__status', 'id').prefetch_related('subscribekeyword_set__keyword').order_by('-datetime')
    
    # 필터링 기준(월, 배송상태)
    if sub_option_month != 'all':
        year, month = map(int, sub_option_month.split('-'))
        subscribes = subscribes.filter(datetime__year=year, datetime__month=month)
    if sub_option_deliverystatus != 'all':
        subscribes = subscribes.filter(delivery__status=int(sub_option_deliverystatus))
        
    sub_months_queryset = Subscribe.objects.annotate(year=ExtractYear('datetime'),month=ExtractMonth('datetime')).values('year', 'month').distinct().order_by('-year', '-month')
    sub_months = [f"{entry['year']}-{entry['month']:02d}" for entry in sub_months_queryset]
    
    paginator = Paginator(subscribes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context={
        'keywords':keywords,
        'keyword_months':keyword_months,
        'sort_option_month':sort_option_month,
        'form':form,
        'subscribes':page_obj,
        'sub_months':sub_months,
        'sub_option_month':sub_option_month,
        'sub_option_deliverystatus':sub_option_deliverystatus,
    }
    return render(request, 'seller/subscribe_index.html', context)

# 환불관리
@login_required
def refund_index(request):
    sort_option_month = request.GET.get('sort-options-month', 'all')
    sort_option_refundstatus = request.GET.get('sort-options-refundstatus', 'all')
    ordercarts = OrderCart.objects.filter(Q(status=2) | Q(status=3)).select_related('order', 'cart__user', 'cart__item').only('order__datetime', 'cart__user__username', 'cart__item__name','status').order_by('-order__datetime')

    # 필터링 기준
    if sort_option_month != 'all':
        year, month = map(int, sort_option_month.split('-'))
        ordercarts = ordercarts.filter(order__datetime__year=year, order__datetime__month=month)
    if sort_option_refundstatus != 'all':
        ordercarts = ordercarts.filter(status=int(sort_option_refundstatus))
        
    months_queryset = Order.objects.annotate(year=ExtractYear('datetime'),month=ExtractMonth('datetime')).values('year', 'month').distinct().order_by('-year', '-month')
    months = [f"{entry['year']}-{entry['month']:02d}" for entry in months_queryset]
    
    paginator = Paginator(ordercarts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'ordercarts':page_obj,
        'months':months,
        'sort_option_month': sort_option_month,
        'sort_option_refundstatus':sort_option_refundstatus
    }
    return render(request, 'seller/refund_index.html', context)

def get_postgresql_uri():
    db_settings = settings.DATABASES['default']
    username = db_settings['USER']
    password = db_settings['PASSWORD']
    host = db_settings['HOST']
    port = db_settings['PORT']
    database = db_settings['NAME']
    
    pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
    return pg_uri

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


@login_required
def review_analysis(request, pk):
    item = get_object_or_404(Item, pk=pk)
    reviews = Review.objects.filter(item=item)
    
    # 데이터베이스 설정
    pg_uri = get_postgresql_uri()
    db = SQLDatabase.from_uri(pg_uri)
    
    # LLM 설정
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)
    
    # SQL 쿼리 및 체인 설정
    execute_query = QuerySQLDataBaseTool(db=db)
    write_query = create_sql_query_chain(llm, db)
    
    answer_prompt = PromptTemplate.from_template(
        """주어진 유저 질문에 대해서, corresponding SQL query, and SQL result, answer the user question.
        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
    )
    
    parser = StrOutputParser()
    
    answer = answer_prompt | llm | parser
    
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer
    )
    
    question = f"item id가{pk}인 리뷰들은 한개의 향수에 대해서 고객들이 남긴리뷰야 니가 판매자라고했을때 이리뷰들의 내용을 한줄로 정리하고 향수의 문제점이있다면 무엇인지 말해줘"
    response = chain.invoke({"question": question})
    

    return JsonResponse({"message": f"{response}"})
# # 데이터 시각화
# def plot_subscription_trend(request):
#     # 월별 구독자 수 집계
#     subscriptions = Subscribe.objects.all().extra(select={'month': "TO_CHAR(datetime, 'YYYY-MM')"}).values('month').annotate(count=Count('id')).order_by('month')
#     # 데이터프레임으로 변환
#     df = pd.DataFrame(subscriptions)
#     # Plotly 그래프 생성
#     fig = px.line(df, x='month', y='count', title='월별 구독자 수 추이', markers=True, labels={'month': '월', 'count': '구독자 수'})
#     fig.update_layout(template='plotly_white', width=800,height=500, font_size=16,)
#     fig.update_traces(line_color= '#5B574F', line_width= 4,)
#     # 그래프를 HTML로 변환
#     graph_html = fig.to_html(full_html=False)
    
#     # 월별 키워드 점유율
#     data = get_monthly_keyword_distribution()
#     months = list(data.keys())
#     default_chart = generate_pie_chart(data, months[0])

#     context={
#         'graph_html': graph_html,
#         'months':months,
#         'default_chart':default_chart,
#         'data':data,
#     }
#     return render(request, 'seller/plot.html', context)


# def get_monthly_keyword_distribution():
#     sub = SubscribeKeyword.objects.annotate(
#         month=ExtractMonth('keyword__month'),
#         year=ExtractYear('keyword__month')
#     ).values('month', 'year', 'keyword__word').annotate(count=Count('id')).order_by('year', 'month', 'count')
    
#     data = {}
#     for entry in sub:
#         year_month = f"{entry['year']}-{entry['month']:02d}"
#         if year_month not in data:
#             data[year_month] = []
#         data[year_month].append({
#             'keyword': entry['keyword__word'],
#             'count': entry['count']
#         })
    
#     return data

# def generate_pie_chart(data, month):
#     df = pd.DataFrame(data[month])
#     fig = px.pie(df, names='keyword', values='count', title=f"{month} 키워드 비중")
    
#     fig.update_layout(
#         template='plotly_white',
#         width=800,height=500,
#         font_size=16,
#     )
    
#     fig.update_traces(textposition='outside',textinfo='label+percent', textfont_size=16,textfont_color="black")
    
#     return fig.to_html(full_html=False)