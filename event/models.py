from django.db import models
from django.contrib.auth.models import User

class Franding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    intensity = models.CharField(max_length=100)
    season = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    age_range = models.CharField(max_length=100)
    price_range = models.CharField(max_length=100)
    cat1 = models.CharField(max_length=100)
    cat2 = models.CharField(max_length=100)