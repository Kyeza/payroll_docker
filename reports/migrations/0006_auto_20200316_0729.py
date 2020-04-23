# Generated by Django 2.2 on 2020-03-16 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20200130_1122'),
        ('reports', '0005_bankreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankreport',
            name='agresso_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='cashreport',
            name='agresso_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='taxationreport',
            name='agresso_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='taxationreport',
            name='deductions',
            field=models.ManyToManyField(related_name='deductions_to_show', to='users.PayrollProcessors'),
        ),
        migrations.AlterField(
            model_name='taxationreport',
            name='earnings',
            field=models.ManyToManyField(related_name='earnings_to_show', to='users.PayrollProcessors'),
        ),
    ]
