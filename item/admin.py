from django.contrib import admin
from .models import Category1, Category2, Brand, Size, ItemType, Item  # 모델 import

# 간단하게 모델을 admin에 등록하는 방법
admin.site.register(Category1)
admin.site.register(Category2)
admin.site.register(Brand)
admin.site.register(Size)
admin.site.register(ItemType)

# 더 많은 설정을 위해 Item 모델에 대한 ModelAdmin 클래스를 정의할 수 있습니다.
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'item_type', 'size', 'price', 'inventory')  # 관리자 페이지에서 보여줄 필드
    list_filter = ('brand', 'item_type', 'size')  # 필터 옵션 추가
    search_fields = ('name', 'summary', 'description')  # 검색 기능 추가

# Item 모델을 ItemAdmin 설정과 함께 등록
admin.site.register(Item, ItemAdmin)
# Register your models here.