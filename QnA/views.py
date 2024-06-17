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
            # return redirect(reverse('QnA:question_list', args=[item_id]))
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
    period = request.GET.get('period', '3days')
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
def item_id_list(Questions, attributes):
    """item_id 전체 조회"""

    Question_list = []
    for item in Questions:
        if attributes == 'id':
            Question_list.append(item.id)
        elif attributes == 'name':
            Question_list.append(item.name)
        elif attributes == 'summary':
            Question_list.append(item.summary)
        elif attributes == 'description':
            Question_list.append(item.description)

    return Question_list


# QnA 데이트 프레임 만들기
def QnA_dataFrame():
    items = Question.objects.all()  # Query all qna from the database
    item_id = item_id_list(items, attributes='id')
    name = item_id_list(items, attributes='name')
    summary = item_id_list(items, attributes='summary')
    description = item_id_list(items, attributes='description')

    data = {
        'item_id': item_id,
        'name': name,
        'summary': summary,
        'description': description,
    }

    df = pd.DataFrame(data)

    return df


def item_csv_file_save():
    df = QnA_dataFrame()
    df.to_csv('QnA.csv', index=False)