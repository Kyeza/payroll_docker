# Generated by Django 2.2.7 on 2019-11-13 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20191113_0916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeemovement',
            name='hours',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
