from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Category1(models.Model):
    name = models.CharField(max_length=50)
    
class DetailCategory2(models.Model):
    name = models.CharField(max_length=50)
    
class Category2(models.Model):
    gender = models.BooleanField()
    detail_cat2 = models.ForeignKey(DetailCategory2, on_delete=models.CASCADE)
    
class Brand(models.Model):
    name = models.CharField(max_length=50)
    
class Size(models.Model):
    ml = models.IntegerField
    
class ItemType(models.Model):
    name = models.CharField(max_length=50)
    
class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cat1 = models.ForeignKey(Category1, on_delete=models.CASCADE)
    cat2 = models.ForeignKey(Category2, on_delete=models.DO_NOTHING)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    item_type=models.ForeignKey(ItemType, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    inventory = models.IntegerField(default=0)
    summary = models.CharField(max_length=250)
    description = models.TextField()
    image = models.URLField()
    