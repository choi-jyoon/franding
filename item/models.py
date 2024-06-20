from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Category1(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Category2(models.Model):
    name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Size(models.Model):
    ml = models.IntegerField(default=50)

    def __str__(self):
        return str(self.ml) + 'ml'
        
    
class ItemType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
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
    image = models.ImageField(upload_to='media/', max_length=255, null=True)
    back_image = models.URLField(max_length=500, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    views = models.IntegerField(default=0)  # 조회수

    def __str__(self):
        
        return self.name
    
class ItemViewCount(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date = models.DateField()
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('item', 'date')