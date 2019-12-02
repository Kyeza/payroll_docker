# Generated by Django 2.2.7 on 2019-11-13 12:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20191113_0917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeemovement',
            name='hours',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
