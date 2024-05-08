from django import forms

class PerfumeForm(forms.Form):
    intensity = forms.ChoiceField(choices=[('subtle', 'Subtle'), ('strong', 'Strong')])
    season = forms.ChoiceField(choices=[('spring', 'Spring'), ('summer', 'Summer'), ('fall', 'Fall'), ('winter', 'Winter'), ('all season', 'all season')])
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('unisex', 'Unisex')])
    age_range = forms.ChoiceField(choices=[('~19', '19세 이하'), ('(20~24)', '20~24'), ('(25~29)', '25~29'), ('(30~34)', '30~34'), ('35~', '35세 이상')])
    price_range = forms.ChoiceField(choices=[('1', '7만원 이하'), ('2', '7~15만원'), ('3', '15~22만원'), ('4', '22만원 이상'), ('5', '상관없음')])
    cat1 = forms.ChoiceField(choices=[('시트러스', '시트러스'), ('플로럴', '플로럴'), ('스위트', '스위트'), ('우디', '우디'), ('머스크', '머스크')])
    cat2 = forms.ChoiceField(choices=[('Lovely', 'Lovely'), ('Casual', 'Casual'), ('Cool', 'Cool'), ('Femine', 'Femine')])