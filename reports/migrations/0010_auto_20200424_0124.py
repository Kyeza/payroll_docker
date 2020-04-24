# Generated by Django 2.2.7 on 2020-04-24 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0009_auto_20200424_0012'),
    ]

    operations = [
        migrations.AddField(
            model_name='extrasummaryreportinfo',
            name='agresso_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='extrasummaryreportinfo',
            name='cost_centre',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='extrasummaryreportinfo',
            name='duty_station',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
