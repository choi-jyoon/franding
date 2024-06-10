from django import forms
from item.models import Item
from review.models import ReviewReply

class ItemForm(forms.ModelForm):
    
    class Meta:
        model = Item
        fields = [
            'cat1', 'cat2', 'brand', 'item_type', 'size', 'name', 'price', 
            'inventory', 'summary', 'description', 'image'
        ]
        labels = {
            'cat1': '카테고리 1',  # 카테고리 1
            'cat2': '카테고리 2',  # 카테고리 2
            'brand': '브랜드',  # 브랜드
            'item_type': '상품 유형',  # 아이템 유형
            'size': '크기 (ml)',  # 크기 (ml)
            'name': '상품명 ',  # 아이템 이름
            'price': '가격(₩)',  # 가격
            'inventory': '재고',  # 재고
            'summary': '요약',  # 요약
            'description': '설명',  # 설명
            'image': '이미지 업로드'  # 이미지 URL
        }
        help_texts = {
            'cat1': '',  # 아이템의 주요 카테고리를 선택하세요.
            'cat2': '',  # 성별 특정성을 포함한 보조 카테고리를 선택하세요.
            'brand': '',  # 아이템의 브랜드를 선택하세요.
            'item_type': '',  # 퍼퓸, 코롱 등과 같은 아이템의 유형을 정의하세요.
            'size': '',  # 밀리리터 단위로 아이템의 크기를 입력하세요.
            'inventory': '',  # 재고에 있는 아이템의 수량을 입력하세요.
            'image': ''  # 제품 이미지를 업로드해주세요.
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15}),  # 설명을 위한 텍스트 영역 설정
            'image': forms.FileInput(), # 이미지 파일필드
        }

class ReviewReplyForm(forms.ModelForm):
    class Meta:
        model = ReviewReply
        fields = ['comment']