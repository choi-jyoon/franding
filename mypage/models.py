from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserAddInfo(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)     # 1대1 관계
    postcode = models.CharField(max_length=6, null=True)
    address = models.TextField(null=True)
    detailAddress = models.CharField(max_length=100, null=True)
    extraAddress = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=20)
    profile_img = models.URLField(null=True, default=' ')
    membership = models.BooleanField(default=False)