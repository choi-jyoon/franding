from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime, timedelta

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
    
class EmailToken(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires_at = datetime.now() + timedelta(days=1)
        super().save(*args, **kwargs)
