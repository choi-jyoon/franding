from django import forms
from .models import Question, Answer

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['id', 'item_id', 'title', 'content']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'user_id', 'content']
