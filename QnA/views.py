from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import FAQ
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.paginator import Paginator
# from time_logger import time_logger
import pandas as pd
from my_langchain.search.search_db import search_question
from django.core.cache import cache
import redis


# Create your views here.

# 3.6959502696990967초
# @time_logger(category='question_create')
def question_create(request, item_id):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user_id_id= request.user.id
            question.item_id.id = item_id
            question.save()            

            return redirect(reverse('QnA:home'))
            
    else:
        form = QuestionForm(initial={'item_id': item_id})
    return render(request, 'QnA/question_form.html', {'form': form})


#0.8915925025939941초
# @time_logger(category='home')
def home(request):
    questions_list = Question.objects.filter(user_id=request.user).order_by('-created_at')  # 모든 질문을 가져옵니다.
    paginator = Paginator(questions_list, 3)  # Show 5 questions per page.

    page_number = request.GET.get('page')
    questions = paginator.get_page(page_number)
    
    return render(request, 'QnA/home.html', {'questions': questions})


#1.6454458236694336초
# @time_logger(category='answer_detail')
def answer_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.filter(question=question)  # question_id를 기반으로 답변을 가져옵니다.
    return render(request, 'QnA/answer_detail.html', {'answers': answers, 'question': question})


# 3.2776596546173096, 0.7485513687133789초
# @time_logger(category='seller_questions')
def seller_questions(request):    

    # 작성일자에 따른 필터링
    
    period = request.GET.get('period', '3weeks')
    now = datetime.now()

    if period == '1day':
        start_date = now - timedelta(days=1)
    elif period == '3days':
        start_date = now - timedelta(days=3)
    elif period == '1week':
        start_date = now - timedelta(weeks=1)
    elif period == '3weeks':
        start_date = now - timedelta(weeks=3)
    else:
        start_date = now - timedelta(days=9999)  # default to 3 days

    questions_period_filter = Question.objects.filter(created_at__gte=start_date).order_by('is_answered','-created_at')

    # 답변 여부에 따른 필터링
    answered_filter = request.GET.get('answered')
    if answered_filter == 'answered':
        questions = questions_period_filter.filter(is_answered=True)
    elif answered_filter == 'unanswered':
        questions = questions_period_filter.filter(is_answered=False)
    else:
        questions = questions_period_filter

    paginator = Paginator(questions, 6)  # Show 6 questions per page.

    page_number = request.GET.get('page')
    questions = paginator.get_page(page_number)

    return render(request, 'QnA/seller_questions.html', {'questions': questions})


# 2.2899374961853027, 0.4439544677734375,초
# @time_logger(category='answer_question')
def answer_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    # answers = get_object_or_404(Answer, id=question_id)
    answers = Answer.objects.filter(question=question)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.user_id_id= request.user.id
            question.is_answered = True
            answer.save()
            question.save()
            return redirect('QnA:seller_questions')
    form = AnswerForm()
    return render(request, 'QnA/seller_answer_form.html', {'form': form, 'question' : question, 'answers': answers})



# QnA 데이터 리스트 만들기
def question_attributes_list(Questions, attributes):
    """question field 전체 조회"""

    Question_list = []
    for ques in Questions:
        if attributes == 'id':
            Question_list.append(ques.id)
        elif attributes == 'title':
            Question_list.append(ques.title)
        elif attributes == 'content':
            Question_list.append(ques.content)
        elif attributes == 'created_at':
            Question_list.append(ques.created_at)

    return Question_list


# QnA 데이트 프레임 만들기
def QnA_dataFrame():
    questions = Question.objects.all()  # Query all qna from the database
    id = question_attributes_list(questions, attributes='id')
    title = question_attributes_list(questions, attributes='title')
    content = question_attributes_list(questions, attributes='content')
    created_at = question_attributes_list(questions, attributes='created_at')

    data = {
        'id': id,
        'title': title,
        'content': content,
        'created_at': created_at,
    }

    df = pd.DataFrame(data)

    return df


# 검색에 사용할 question csv 파일 생성
def question_csv_file_save():
    df = QnA_dataFrame()
    df.to_csv('my_langchain/csv_file/QnA.csv', index=False)    


# search_db의 답변을 리스트로 반환
def search_db_attr(search_db_answer):
    search_db_rt_list=[]
    search_db_results = search_db_answer['results']

    for result in search_db_results:
        search_db_rt = result.page_content
        search_db_rt_list.append(search_db_rt)

    return search_db_rt_list


# ,앞부분까지 쪼개기
def split_title(result_list):
    """ search_db_attr """

    rt_list_id = []
    for result in result_list:
        s_result = result.split(',')[0]
        int_s_result = int(s_result)
        rt_list_id.append(int_s_result)

    return rt_list_id

# split_title(search_db_attr(search_question()))


# search_db llm모델 답변 읽어서 데이터베이스에 있는 질문 제목이랑 비교해서 질문 id반환 
def f_search_question(query):
    """ 검색하려면 이거 호출하면 됨 """

    sh_question = search_question(query)
    sh_attr = search_db_attr(sh_question)
    all_questions = Question.objects.all()
    search_question_list = []

    for ques in all_questions:
        filter_id = ques.id
        for s_db_attr in split_title(sh_attr):
            if filter_id == s_db_attr:
                search_question_list.append(ques)

    return search_question_list


# 레디스 연결 상태 확인
def redis_connect():
    """ 레디스 연결 상태 확인 """

    try:
        r = redis.Redis(host='127.0.0.1', port=6379/1)
        r.ping()
        print("Redis에 성공적으로 연결되었습니다.")
    except redis.exceptions.ConnectionError as e:
        print(f"Redis 연결 실패: {e}")

def redis_connect2():
    """ 레디스 연결 상태 확인 """

    r = redis.StrictRedis(
    host='52.79.153.140',
    port=16379,
    decode_responses=True
    )

    print(r.ping())  # PONG 출력


# 캐시 키 생성
def cache_key_create(search_word):
    """ 캐시 키 생성 """

    modified_search_word = search_word.replace(' ', '_')

    return modified_search_word


# 캐시에 키 생성
def cache_data(langchain_func, key_name, cache_time, search_word=None):
    """ 캐시에 데이터 저장 """

    cache_key = cache_key_create(key_name)
    cached_data = cache.get(cache_key)

    # 캐시 없으면 데이터 저장
    if not cached_data:

        # 예외 처리
        if search_word is None:
            func_value = langchain_func()
        else:
            func_value = langchain_func(search_word)     
        
        # 캐시에 데이터 저장
        cache.set(cache_key, func_value, cache_time)  # 72시간

        return func_value        
    
    return cached_data


# 검색
def qna_search(request):    

    # 검색 여부에 따른 필터링
    search_word = request.GET.get('search', '') or request.POST.get('search', '')

    results = cache_data(key_name=search_word, search_word=search_word, langchain_func=f_search_question, cache_time=60*60*24*365)  # 검색 조건 수정 필요    

    paginator = Paginator(results, 6)  # Show 6 questions per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'QnA/qna_search.html', {'page_obj': page_obj, 'search_word': search_word})       

    

    