from django.core.exceptions import ValidationError
from django.db import models

from payroll.models import PayrollPeriod
from users.models import Employee


class ExTraSummaryReportInfo(models.Model):
    key = models.CharField(max_length=150, blank=True, default=None, unique=True, primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name='report')
    analysis = models.CharField(max_length=150, null=True, blank=True)
    employee_name = models.CharField(max_length=250, null=True, blank=True)
    job_title = models.CharField(max_length=150, null=True, blank=True)
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.SET_NULL, null=True)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=None,)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=None,)
    gross_earning = models.DecimalField(max_digits=12, decimal_places=2, default=None,)

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

