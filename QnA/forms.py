from django import forms
from .models import Question, Answer1

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['id', 'product_id', 'user_id', 'title', 'content']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer1
        fields = ['id', 'question', 'product_id', 'user_id', 'content']
