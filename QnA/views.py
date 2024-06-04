from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.

def question_list(request, product_id):
    questions = Question.objects.filter(product_id=product_id)
    return render(request, 'QnA/question_list.html', {'questions': questions})

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
            question.user = request.user
            question.item_id.id = item_id
            question.save()            
            return redirect(reverse('QnA:question_list', args=[item_id]))
    else:
        form = QuestionForm()
    return render(request, 'QnA/question_form.html', {'form': form})
