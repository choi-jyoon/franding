from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import FAQ
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.paginator import Paginator

# Create your views here.

def question_list(request, item_id):
    # questions = Question.objects.filter(item_id=item_id)
    questions = Question.objects.all().order_by('-created_at')  # 모든 질문을 가져옵니다.
    answers = Answer.objects.all().order_by('-created_at')
    return render(request, 'QnA/question_list.html', {'questions': questions, 'answers': answers})

def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'GET':
        form = AnswerForm(request.GET)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.user = request.user
            answer.question = question
            answer.save()
            return redirect('QnA:question_detail', question_id=question.id)
    else:
        form = AnswerForm()
    return render(request, 'QnA/question_detail.html', {'question': question, 'form': form})

def question_create(request, item_id):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user_id_id= request.user.id
            question.item_id.id = item_id
            question.save()            
            return redirect(reverse('QnA:question_list', args=[item_id]))
            # return redirect(reverse('QnA:question_list'))
            
    else:
        form = QuestionForm(initial={'item_id': item_id})
    return render(request, 'QnA/question_form.html', {'form': form})


def home(request):
    questions = Question.objects.filter(user_id=request.user).order_by('-created_at')  # 모든 질문을 가져옵니다.
    return render(request, 'QnA/home.html', {'questions': questions,})


def answer_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.filter(question=question)  # question_id를 기반으로 답변을 가져옵니다.
    return render(request, 'QnA/answer_detail.html', {'answers': answers, 'question': question})


def seller_questions(request):
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
        start_date = now - timedelta(days=3)  # default to 3 days

    questions_list = Question.objects.filter(created_at__gte=start_date).order_by('is_answered','-created_at')
    paginator = Paginator(questions_list, 5)  # Show 5 questions per page.

    page_number = request.GET.get('page')
    questions = paginator.get_page(page_number)

    return render(request, 'QnA/seller_questions.html', {'questions': questions})


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