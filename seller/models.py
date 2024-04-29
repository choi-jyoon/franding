from django.db import models  # 장고의 모델을 사용하기 위한 모듈 임포트
from django.contrib.auth.models import User  # 장고의 기본 사용자 모델 임포트
from django import forms  # 장고의 폼 모듈 임포트

class Category1(models.Model):  # 카테고리1 모델 정의
    name = models.CharField(max_length=50)  # 이름 필드

class DetailCategory2(models.Model):  # 세부 카테고리2 모델 정의
    name = models.CharField(max_length=50)  # 이름 필드

class Category2(models.Model):  # 카테고리2 모델 정의
    detail_cat2 = models.ForeignKey(DetailCategory2, on_delete=models.CASCADE)  # 세부 카테고리2와의 관계 설정

class Brand(models.Model):  # 브랜드 모델 정의
    name = models.CharField(max_length=50)  # 이름 필드

class Size(models.Model):  # 사이즈 모델 정의
    ml = models.IntegerField(default=50)  # 밀리리터(ml) 필드

class ItemType(models.Model):  # 아이템 유형 모델 정의
    name = models.CharField(max_length=50)  # 이름 필드

class Item(models.Model):  # 아이템 모델 정의
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')  # 사용자와의 관계 설정, related_name 변경
    cat1 = models.ForeignKey(Category1, on_delete=models.CASCADE)  # 카테고리1과의 관계 설정
    cat2 = models.ForeignKey(Category2, on_delete=models.CASCADE)  # 카테고리2와의 관계 설정
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)  # 브랜드와의 관계 설정
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE)  # 아이템 유형과의 관계 설정
    size = models.ForeignKey(Size, on_delete=models.CASCADE)  # 사이즈와의 관계 설정
    name = models.CharField(max_length=50)  # 이름 필드
    price = models.IntegerField()  # 가격 필드
    inventory = models.IntegerField(default=0)  # 재고 필드, 기본값 0 설정
    summary = models.CharField(max_length=250)  # 요약 필드
    description = models.TextField()  # 설명 필드
    image = models.URLField()  # 이미지 URL 필드

class ViewItem(models.Model):  # 아이템 조회 모델 정의
    name = models.CharField(max_length=100)  # 이름 필드
    description = models.TextField()  # 설명 필드
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 가격 필드

class Product(models.Model):  # 제품 모델 정의
    name = models.CharField(max_length=100)  # 이름 필드
    description = models.TextField()  # 설명 필드
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 가격 필드

    def __str__(self):  # 문자열 반환 메서드 재정의
        return self.name  # 이름 반환

    @classmethod  # 클래스 메서드 데코레이터
    def search(cls, query):  # 검색 클래스 메서드 정의
        return cls.objects.filter(name__icontains=query) | cls.objects.filter(description__icontains=query)  # 이름 또는 설명에 쿼리가 포함된 제품 필터링

class Review(models.Model):  # 리뷰 모델 정의
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # 제품과의 관계 설정
    author = models.CharField(max_length=100)  # 작성자 필드
    text = models.TextField()  # 내용 필드
    rating = models.IntegerField()  # 평점 필드

    def __str__(self):  # 문자열 반환 메서드 재정의
        return f"{self.product} 리뷰 - 작성자: {self.author}, 평점: {self.rating}"  # 리뷰 정보 문자열 반환

class Order(models.Model):  # 주문 모델 정의
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # 제품과의 관계 설정
    customer_name = models.CharField(max_length=100)  # 고객 이름 필드
    quantity = models.PositiveIntegerField()  # 수량 필드, 양수 값만 허용
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # 총 가격 필드
    ordered_at = models.DateTimeField(auto_now_add=True)  # 주문 일시 필드, 자동으로 현재 시간으로 설정

    def __str__(self):  # 문자열 반환 메서드 재정의
        return f"{self.product} 주문 - 고객: {self.customer_name}, 수량: {self.quantity}, 주문 일시: {self.ordered_at}"  # 주문 정보 문자열 반환

class ItemForm(forms.ModelForm):  # 아이템 폼 정의
    class Meta:  # 메타 클래스 정의
        model = Item  # 모델 지정
        fields = [  # 폼 필드 목록 지정
            'cat1', 'cat2', 'brand', 'item_type', 'size', 'name', 'price', 
            'inventory', 'summary', 'description', 'image'
        ]
        labels = {  # 레이블 지정
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
        help_texts = {  # 도움말 텍스트 지정
            'cat1': 'Select the primary category for the item.',  # 아이템의 주요 카테고리를 선택하세요.
            'cat2': 'Select the secondary category, including gender specificity.',  # 성별 특정성을 포함한 보조 카테고리를 선택하세요.
            'brand': 'Select the brand of the item.',  # 아이템의 브랜드를 선택하세요.
            'item_type': 'Define the type of item, such as Eau de Parfum, Cologne, etc.',  # 향수, 코LOGNE 등과 같은 아이템의 유형을 정의하세요.
            'size': 'Enter the size of the item in milliliters.',  # 밀리리터 단위로 아이템의 크기를 입력하세요.
            'inventory': 'Enter the number of items available in stock.',  # 재고에 있는 아이템의 수량을 입력하세요.
            'image': 'Enter the URL where the image of the product is hosted.'  # 제품 이미지가 호스팅된 URL을 입력하세요.
        }
        widgets = {  # 위젯 지정
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15})  # 설명을 위한 텍스트 영역 설정
        }

