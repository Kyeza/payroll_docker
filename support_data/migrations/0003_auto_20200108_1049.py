# Generated by Django 2.2.7 on 2020-01-08 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support_data', '0002_auto_20191105_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tax',
            name='year',
            field=models.IntegerField(choices=[(2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026), (2027, 2027), (2028, 2028), (2029, 2029)], default=2020),
        ),
    ]