from django.core.exceptions import ValidationError
from django.db import models

from payroll.models import PayrollPeriod
from users.models import Employee


class ExTraSummaryReportInfo(models.Model):
    key = models.CharField(max_length=150, blank=True, default=None, unique=True, primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name='report', null=True)
    analysis = models.CharField(max_length=150, null=True, blank=True)
    employee_name = models.CharField(max_length=250, null=True, blank=True)
    job_title = models.CharField(max_length=150, null=True, blank=True)
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.SET_NULL, null=True)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=None, )
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=None, )
    gross_earning = models.DecimalField(max_digits=12, decimal_places=2, default=None, )

    def clean(self):
        if self.key is None:
            key = f'{self.payroll_period.payroll_key}S{self.employee.pk}'
            if ExTraSummaryReportInfo.objects.filter(key=key):
                raise ValidationError('Duplicate record')
            else:
                self.key = key

        if self.total_deductions is not None:
            self.total_deductions = round(self.total_deductions)

        if self.net_pay is not None:
            self.net_pay = round(self.net_pay)

        if self.gross_earning is not None:
            self.gross_earning = round(self.gross_earning)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.employee}'


class NSSFReport(models.Model):
    report_key = models.CharField(max_length=150, blank=True, default=None, unique=True, primary_key=True)
    employee_id = models.IntegerField()
    payroll_period = models.ForeignKey('payroll.PayrollPeriod', on_delete=models.CASCADE, null=True, blank=True)
    agresso_number = models.CharField(max_length=30, null=True, blank=True)
    nsif_or_nssf_number = models.CharField(max_length=30, null=True, blank=True)
    employee_full_name = models.CharField(max_length=300, null=True, blank=True)
    duty_station = models.CharField(max_length=100, null=True, blank=True)
    cost_centre = models.CharField(max_length=30, null=True, blank=True)
    job_title = models.CharField(max_length=150, null=True, blank=True)
    user_extra_report = models.ForeignKey(ExTraSummaryReportInfo, on_delete=models.CASCADE, null=True, blank=True)
    earnings_and_deductions = models.ManyToManyField('users.PayrollProcessors', blank=True)

    @property
    def total_social_security(self):
        total = 0
        if self.earnings_and_deductions.count() > 0:
            total = sum([amt[0] for amt in list(self.earnings_and_deductions.values_list('amount'))])
        return total

    def clean(self):
        if self.report_key is None:
            key = f'{self.payroll_period.payroll_key}S{self.employee_id}'
            if NSSFReport.objects.filter(report_key=key):
                raise ValidationError('Duplicate record')
            else:
                self.report_key = key

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.employee_full_name}'
