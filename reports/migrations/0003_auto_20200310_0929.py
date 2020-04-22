# Generated by Django 2.2 on 2020-03-10 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20200130_1122'),
        ('reports', '0002_auto_20191105_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='extrasummaryreportinfo',
            name='earnings',
            field=models.ManyToManyField(to='users.PayrollProcessors'),
        ),
        migrations.CreateModel(
            name='TaxationReport',
            fields=[
                ('report_id', models.CharField(editable=False, max_length=50, primary_key=True, serialize=False)),
                ('period', models.CharField(blank=True, max_length=20, null=True)),
                ('staff_full_name', models.CharField(blank=True, max_length=200, null=True)),
                ('cost_centre', models.CharField(blank=True, max_length=15, null=True)),
                ('tin_number', models.CharField(blank=True, max_length=30, null=True)),
                ('gross_pay', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('earnings', models.ManyToManyField(to='users.PayrollProcessors')),
            ],
        ),
        migrations.CreateModel(
            name='SocialSecurityReport',
            fields=[
                ('report_id', models.CharField(editable=False, max_length=50, primary_key=True, serialize=False)),
                ('period', models.CharField(blank=True, max_length=20, null=True)),
                ('agresso_number', models.CharField(blank=True, max_length=15, null=True)),
                ('social_security_number', models.CharField(blank=True, max_length=25, null=True)),
                ('staff_full_name', models.CharField(blank=True, max_length=200, null=True)),
                ('duty_station', models.CharField(blank=True, max_length=150, null=True)),
                ('cost_centre', models.CharField(blank=True, max_length=15, null=True)),
                ('job_title', models.CharField(blank=True, max_length=200, null=True)),
                ('earnings', models.ManyToManyField(to='users.PayrollProcessors')),
                ('summary_report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reports.ExTraSummaryReportInfo')),
            ],
        ),
        migrations.CreateModel(
            name='CashReport',
            fields=[
                ('report_id', models.CharField(editable=False, max_length=50, primary_key=True, serialize=False)),
                ('period', models.CharField(blank=True, max_length=15, null=True)),
                ('staff_full_name', models.CharField(blank=True, max_length=200, null=True)),
                ('job_title', models.CharField(blank=True, max_length=200, null=True)),
                ('payment_location', models.CharField(blank=True, max_length=200, null=True)),
                ('payment_type', models.CharField(blank=True, max_length=20, null=True)),
                ('summary_report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reports.ExTraSummaryReportInfo')),
            ],
        ),
        migrations.CreateModel(
            name='BankReport',
            fields=[
                ('report_id', models.CharField(editable=False, max_length=50, primary_key=True, serialize=False)),
                ('period', models.CharField(blank=True, max_length=15, null=True)),
                ('staff_full_name', models.CharField(blank=True, max_length=200, null=True)),
                ('payment_location', models.CharField(blank=True, max_length=200, null=True)),
                ('bank', models.CharField(blank=True, max_length=200, null=True)),
                ('branch', models.CharField(blank=True, max_length=150, null=True)),
                ('sort_code', models.CharField(blank=True, max_length=15, null=True)),
                ('account_number', models.CharField(blank=True, max_length=30, null=True)),
                ('summary_report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reports.ExTraSummaryReportInfo')),
            ],
        ),
    ]
