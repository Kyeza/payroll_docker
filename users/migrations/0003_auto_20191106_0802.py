# Generated by Django 2.2.7 on 2019-11-06 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20191106_0755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='assigned_locations',
            field=models.ManyToManyField(blank=True, related_name='assigned_locations', to='support_data.DutyStation'),
        ),
    ]
