from django.contrib import admin
from .models import ScentCategory, ScentNote

@admin.register(ScentCategory)
class ScentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(ScentNote)
class ScentNoteAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
