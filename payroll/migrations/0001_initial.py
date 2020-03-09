# Generated by Django 2.2 on 2020-03-06 09:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank', models.CharField(max_length=150)),
                ('branch', models.CharField(blank=True, max_length=200, null=True)),
                ('sort_code', models.CharField(blank=True, max_length=100, null=True)),
                ('bank_code', models.CharField(blank=True, max_length=3, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=150)),
                ('description', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='EarningDeductionCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='EarningDeductionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ed_type', models.CharField(max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=150, null=True)),
                ('account_name', models.CharField(blank=True, max_length=200, null=True)),
                ('recurrent', models.CharField(choices=[('YES', 'Yes'), ('NO', 'No')], max_length=3)),
                ('taxable', models.CharField(choices=[('YES', 'Yes'), ('NO', 'No')], max_length=3)),
                ('export', models.CharField(blank=True, choices=[('YES', 'Yes'), ('NO', 'No')], default='NO', max_length=3, null=True)),
                ('factor', models.FloatField(blank=True, default=0, null=True)),
                ('summarize', models.CharField(choices=[('YES', 'Yes'), ('NO', 'No')], default='NO', max_length=3, null=True)),
                ('agresso_type', models.CharField(blank=True, choices=[('STAFF EXPENSES', 'STAFF EXPENSES'), ('SEVERANCE PAYMENTS', 'SEVERANCE PAYMENTS'), ('SALARY COSTS', 'SALARY COSTS'), ('SALARIES', 'SALARIES'), ('PENSION COSTS', 'PENSION COSTS'), ('STAFF ADVANCES', 'STAFF ADVANCES'), ('EMPLOYEE PENSION', 'EMPLOYEE PENSION'), ('EMPLOYER PENSION', 'EMPLOYER PENSION'), ('HARDSHIP', 'HARDSHIP'), ('ACCRUED PAYROLL', 'ACCRUED PAYROLL'), ('SOCIAL SECURITY', 'SOCIAL SECURITY'), ('SALARY COSTS', 'SALARY COSTS'), ('OVERTIME', 'OVERTIME'), ('PAYE', 'PAYE'), ('LOAN', 'LOAN'), ('PAYROLL DEDUCTIONS', 'PAYROLL DEDUCTIONS')], max_length=50, null=True)),
                ('account_code', models.CharField(blank=True, max_length=15, null=True)),
                ('debit_credit_sign', models.CharField(blank=True, max_length=15, null=True)),
                ('display_number', models.IntegerField(blank=True, default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LSTRates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lower_boundary', models.DecimalField(decimal_places=2, max_digits=12)),
                ('upper_boundary', models.DecimalField(decimal_places=2, max_digits=12)),
                ('fixed_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='PAYERates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lower_boundary', models.DecimalField(decimal_places=2, max_digits=12)),
                ('upper_boundary', models.DecimalField(decimal_places=2, max_digits=12)),
                ('fixed_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='PayrollCenter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('date_create', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(blank=True, max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PayrollCenterEds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pced_key', models.CharField(blank=True, default=None, max_length=150, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PayrollPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(choices=[('JANUARY', 'JANUARY'), ('FEBRUARY', 'FEBRUARY'), ('MARCH', 'MARCH'), ('APRIL', 'APRIL'), ('MAY', 'MAY'), ('JUNE', 'JUNE'), ('JULY', 'JULY'), ('AUGUST', 'AUGUST'), ('SEPTEMBER', 'SEPTEMBER'), ('OCTOBER', 'OCTOBER'), ('NOVEMBER', 'NOVEMBER'), ('DECEMBER', 'DECEMBER')], db_index=True, default='MARCH', max_length=15)),
                ('year', models.IntegerField(choices=[(2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026), (2027, 2027), (2028, 2028), (2029, 2029)], db_index=True, default=2020)),
                ('payroll_key', models.CharField(blank=True, default=None, max_length=150, unique=True)),
                ('status', models.CharField(default='OPEN', max_length=6)),
                ('processing_dollar_rate', models.FloatField(blank=True, null=True, verbose_name='Dollar rate')),
            ],
            options={
                'permissions': [('close_payrollperiod', 'Can close payroll period'), ('process_payrollperiod', 'Can process payroll period')],
            },
        ),
        migrations.CreateModel(
            name='PayrollSummaryApprovals',
            fields=[
                ('approver_names', models.CharField(max_length=300)),
                ('payroll_summary', models.CharField(max_length=300)),
                ('signature', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('date_of_approval', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
    ]
