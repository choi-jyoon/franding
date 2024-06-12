from django.contrib import admin
from .models import Keyword, Subscribe, SubscribeKeyword, SubscribePayInfo
# Register your models here.

admin.site.register(Keyword)
admin.site.register(Subscribe)
admin.site.register(SubscribeKeyword)
admin.site.register(SubscribePayInfo)

