from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from mypage.models import UserAddInfo

class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'email')
        
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