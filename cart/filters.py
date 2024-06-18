from django_filters import rest_framework as filters
from item.models import Item

class ItemFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains') 
    #lookup_expr='icontains'는 대소문자를 구분하지 않고, 해당 필드가 지정된 문자열을 포함하고 있는지 검사합니다. 즉, 이 필터를 사용하면 name 필드에서 부분 일치 검색을 수행할 수 있습니다.
    price_lte = filters.NumberFilter(field_name='price', lookup_expr='lte')
    #lookup_expr='lte' (less than or equal to)는 필드 값이 제공된 값 이하인지 검사합니다. 즉, 이 필터는 price가 쿼리 매개변수로 전달된 값보다 작거나 같은 모든 제품을 반환합니다.
    price_gte = filters.NumberFilter(field_name='price', lookup_expr='gte')
    #lookup_expr='gte' (greater than or equal to)는 필드 값이 제공된 값 이상인지 검사합니다. 이는 price가 쿼리 매개변수로 전달된 값보다 크거나 같은 모든 제품을 반환합니다.
    in_stock = filters.BooleanFilter()
    #이 필터는 in_stock 필드가 True 또는 False인 제품을 필터링하는 데 사용됩니다. 예를 들어, 쿼리에서 in_stock=True를 지정하면 재고가 있는 제품만 반환됩니다.

    class Meta:
        model = Item
        fields = ['id', 'name', 'summary', 'description']