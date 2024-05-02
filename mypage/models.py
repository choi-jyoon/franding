from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserAddInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=50, default='ooo')
    address = models.TextField()
    phone = models.CharField(max_length=20)
    profile_img = models.URLField(null=True, default=' ')