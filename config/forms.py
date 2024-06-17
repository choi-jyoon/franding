from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from mypage.models import UserAddInfo
from django.utils.translation import gettext_lazy as _

class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'email')
       
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': '사용자 ID를 입력하세요',  
        })
        self.fields['first_name'].widget.attrs.update({
            'placeholder': '이름을 입력하세요',  
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': '성을 입력하세요',  
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'franding@example.com',  
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': '비밀번호를 입력하세요',  
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': '비밀번호를 다시 한 번 입력하세요',  
        })
        
    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
        return user

class UserAddInfoForm(forms.ModelForm):
    class Meta:
        model = UserAddInfo
        fields = ('phone',)
        
    def __init__(self, *args, **kwargs):
        super(UserAddInfoForm, self).__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs.update({
            'placeholder': '010-0000-0000',  
        })
        
        

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="ID", max_length=255, widget=forms.TextInput({
        'class': 'form-control',
        'placeholder': 'ID',
    }))
    password = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput({
        'autocomplete': 'current-password',
        'class': 'form-control',
        'placeholder': '비밀번호',
    }))
    
class FindUsernameForm(forms.Form):
    email = forms.EmailField(label='이메일', max_length=254)