from django import forms
from .models import Question, Answer, Item

class QuestionForm(forms.ModelForm):
    # item = forms.ModelChoiceField(queryset=Item.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Question
        fields = ['id', 'item_id', 'title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '질문하실 제목을 입력하세요.'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '문의 내용을 입력하세요.'}),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '답변 내용을 입력하세요.'}),
        }
