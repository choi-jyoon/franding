from django import forms
from item.models import Item


# class ItemForm(forms.ModelForm):
#     class Meta:
#         model = Item
#         fields = '__all__'  # 이렇게 하면 모든 필드를 폼에 포함시킵니다.


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'cat1', 'cat2', 'brand', 'item_type', 'size', 'name', 'price', 
            'inventory', 'summary', 'description', 'image'
        ]
        labels = {
            'cat1': 'Category 1',  # 카테고리 1
            'cat2': 'Category 2',  # 카테고리 2
            'brand': 'Brand',  # 브랜드
            'item_type': 'Type of Item',  # 아이템 유형
            'size': 'Size (ml)',  # 크기 (ml)
            'name': 'Item Name',  # 아이템 이름
            'price': 'Price',  # 가격
            'inventory': 'Inventory',  # 재고
            'summary': 'Summary',  # 요약
            'description': 'Description',  # 설명
            'image': 'Image URL'  # 이미지 URL
        }
        help_texts = {
            'cat1': 'Select the primary category for the item.',  # 아이템의 주요 카테고리를 선택하세요.
            'cat2': 'Select the secondary category, including gender specificity.',  # 성별 특정성을 포함한 보조 카테고리를 선택하세요.
            'brand': 'Select the brand of the item.',  # 아이템의 브랜드를 선택하세요.
            'item_type': 'Define the type of item, such as Eau de Parfum, Cologne, etc.',  # 퍼퓸, 코롱 등과 같은 아이템의 유형을 정의하세요.
            'size': 'Enter the size of the item in milliliters.',  # 밀리리터 단위로 아이템의 크기를 입력하세요.
            'inventory': 'Enter the number of items available in stock.',  # 재고에 있는 아이템의 수량을 입력하세요.
            'image': 'Enter the URL where the image of the product is hosted.'  # 제품 이미지가 호스팅된 URL을 입력하세요.
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15})  # 설명을 위한 텍스트 영역 설정
        }

