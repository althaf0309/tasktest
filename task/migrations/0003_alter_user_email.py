# Generated by Django 5.2 on 2025-04-09 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
