# Generated by Django 5.0.3 on 2024-06-19 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='back_image',
            field=models.URLField(max_length=500, null=True),
        ),
    ]
