# Generated by Django 5.0.3 on 2024-06-04 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mypage', '0004_remove_useraddinfo_user_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddinfo',
            name='membership',
            field=models.BooleanField(default=False),
        ),
    ]
