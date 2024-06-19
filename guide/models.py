from django.db import models

class ScentCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

class ScentNote(models.Model):
    category = models.ForeignKey(ScentCategory, related_name='notes', on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name
