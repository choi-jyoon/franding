from django import forms
from .models import Item

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['id']
