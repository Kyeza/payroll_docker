# Generated by Django 2.2.7 on 2019-12-02 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0002_auto_20191105_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payrollperiod',
            name='month',
            field=models.CharField(choices=[('JANUARY', 'JANUARY'), ('FEBRUARY', 'FEBRUARY'), ('MARCH', 'MARCH'), ('APRIL', 'APRIL'), ('MAY', 'MAY'), ('JUNE', 'JUNE'), ('JULY', 'JULY'), ('AUGUST', 'AUGUST'), ('SEPTEMBER', 'SEPTEMBER'), ('OCTOBER', 'OCTOBER'), ('NOVEMBER', 'NOVEMBER'), ('DECEMBER', 'DECEMBER')], db_index=True, default='DECEMBER', max_length=15),
        ),
    ]
