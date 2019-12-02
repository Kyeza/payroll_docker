import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from hr_system import settings
from hr_system.constants import YES_OR_NO_TYPES
from .constants import MONTHS, PAYROLL_YEARS, KV_MONTH, DISPLAY_NUMS


class EarningDeductionCategory(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


class EarningDeductionType(models.Model):
    AGGRESSO_TYPES = (
        ('STAFF EXPENSES', 'STAFF EXPENSES'),
        ('SEVERANCE PAYMENTS', 'SEVERANCE PAYMENTS'),
        ('SALARY COSTS', 'SALARY COSTS'),
        ('SALARIES', 'SALARIES'),
        ('PENSION COSTS', 'PENSION COSTS'),
        ('STAFF ADVANCES', 'STAFF ADVANCES'),
        ('EMPLOYEE PENSION', 'EMPLOYEE PENSION'),
        ('EMPLOYER PENSION', 'EMPLOYER PENSION'),
        ('HARDSHIP', 'HARDSHIP'),
        ('ACCRUED PAYROLL', 'ACCRUED PAYROLL'),
        ('SOCIAL SECURITY', 'SOCIAL SECURITY'),
        ('SALARY COSTS', 'SALARY COSTS'),
        ('OVERTIME', 'OVERTIME'),
        ('PAYE', 'PAYE'),
        ('LOAN', 'LOAN'),
        ('PAYROLL DEDUCTIONS', 'PAYROLL DEDUCTIONS')
    )
    ed_type = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=150, null=True, blank=True)
    account_name = models.CharField(max_length=200, null=True, blank=True)
    ed_category = models.ForeignKey(EarningDeductionCategory, on_delete=models.DO_NOTHING, null=True, blank=True)
    recurrent = models.CharField(max_length=3, choices=YES_OR_NO_TYPES)
    taxable = models.CharField(max_length=3, choices=YES_OR_NO_TYPES)
    export = models.CharField(max_length=3, choices=YES_OR_NO_TYPES, default=YES_OR_NO_TYPES[1][0], null=True,
                              blank=True)
    factor = models.FloatField(default=0, null=True, blank=True)
    summarize = models.CharField(max_length=3, choices=YES_OR_NO_TYPES, null=True, default=YES_OR_NO_TYPES[1][0])
    agresso_type = models.CharField(max_length=50, null=True, blank=True, choices=AGGRESSO_TYPES)
    account_code = models.CharField(max_length=15, null=True, blank=True)
    debit_credit_sign = models.CharField(max_length=15, null=True, blank=True)
    display_number = models.IntegerField(null=True, blank=True, default=0)

    def get_absolute_url(self):
        return reverse('payroll:ed-type-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.ed_type


class Bank(models.Model):
    """docstring for Bank"""
    bank = models.CharField(max_length=150)
    branch = models.CharField(max_length=200, null=True, blank=True)
    sort_code = models.CharField(max_length=100, null=True, blank=True)
    bank_code = models.CharField(max_length=3, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('payroll:bank-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.bank


class Currency(models.Model):
    """docstring for Currency"""
    currency = models.CharField(max_length=150)
    description = models.CharField(max_length=150)

    def get_absolute_url(self):
        return reverse('payroll:currency-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.currency


class PAYERates(models.Model):
    lower_boundary = models.DecimalField(max_digits=12, decimal_places=2)
    upper_boundary = models.DecimalField(max_digits=12, decimal_places=2)
    fixed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    rate = models.DecimalField(max_digits=12, decimal_places=2)


# Import here to avoid circular imports issue
from support_data.models import Country, Organization


class PayrollCenter(models.Model):
    """docstring for PayrollCenter"""
    name = models.CharField(max_length=150)
    date_create = models.DateTimeField(auto_now=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    description = models.CharField(max_length=150, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET(None), null=True)

    def get_absolute_url(self):
        return reverse('payroll:payroll-center-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class LSTRates(models.Model):
    lower_boundary = models.DecimalField(max_digits=12, decimal_places=2)
    upper_boundary = models.DecimalField(max_digits=12, decimal_places=2)
    fixed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)


class PayrollCenterEds(models.Model):
    payroll_center = models.ForeignKey(PayrollCenter, on_delete=models.CASCADE)
    ed_type = models.ForeignKey(EarningDeductionType, on_delete=models.SET_NULL, null=True)
    pced_key = models.CharField(max_length=150, blank=True, null=False, default=None, unique=True)

    def clean(self):
        if self.pced_key is None:
            pced_key = f'P{self.payroll_center_id}E{self.ed_type_id}'
            if PayrollCenterEds.objects.filter(pced_key=pced_key):
                raise ValidationError(f'Earnings and Deductions already available for this Payroll Center')
            else:
                self.pced_key = pced_key

    def get_absolute_url(self):
        return reverse('payroll:payroll-center-eds-detail', kwargs={'pk': self.pk})

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.payroll_center.name}-{self.ed_type.ed_type}'


class PayrollPeriod(models.Model):
    """docstring for PayrollPeriod"""

    _month = datetime.datetime.now().month
    payroll_center = models.ForeignKey(PayrollCenter, on_delete=models.CASCADE)
    month = models.CharField(max_length=15, choices=MONTHS, default=MONTHS[_month - 1][1], db_index=True)
    year = models.IntegerField(choices=PAYROLL_YEARS, default=datetime.datetime.now().year, db_index=True)
    payroll_key = models.CharField(max_length=150, blank=True, null=False, default=None, unique=True)
    status = models.CharField(max_length=6, default='OPEN')
    processing_dollar_rate = models.FloatField(null=True, blank=True, verbose_name='Dollar rate')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def to_dict(self):
        return {
            'id': self.pk, 'payroll_center': str(self.payroll_center),
            'month': self.month, 'year': self.year, 'payroll_key': self.payroll_key,
            'status': self.status
        }

    def get_absolute_url(self):
        return reverse('payroll:payroll-period-detail', kwargs={'pk': self.pk})

    def clean(self):
        if self.payroll_key is None:
            payroll_key = f'Y{self.year}M{KV_MONTH[self.month]}C{self.payroll_center_id}'
            if PayrollPeriod.objects.filter(payroll_key=payroll_key):
                raise ValidationError(f'Payroll period for this month already created')
            else:
                self.payroll_key = payroll_key

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.payroll_center.name}-{self.payroll_key}'

    class Meta:
        permissions = [
            ("close_payrollperiod", "Can close payroll period"),
            ("process_payrollperiod", "Can process payroll period"),
        ]


class PayrollSummaryApprovals(models.Model):
    approver_names = models.CharField(max_length=300)
    payroll_summary = models.CharField(max_length=300)
    signature = models.CharField(max_length=50, primary_key=True)
    date_of_approval = models.DateField(default=timezone.now)
