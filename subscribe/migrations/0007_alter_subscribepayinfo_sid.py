# Generated by Django 5.0.3 on 2024-06-08 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0006_subscribepayinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribepayinfo',
            name='sid',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
