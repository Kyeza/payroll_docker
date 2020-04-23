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
    earnings_to_display = models.ManyToManyField('users.PayrollProcessors', related_name='earnings')
    deductions_to_display = models.ManyToManyField('users.PayrollProcessors', related_name='deductions')
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=None, )
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=None, )
    gross_earning = models.DecimalField(max_digits=12, decimal_places=2, default=None, )

    def clean(self):
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
        return f'Summary - {self.employee}'


class SocialSecurityReport(models.Model):
    report_id = models.CharField(max_length=50, editable=False, primary_key=True)
    period = models.CharField(max_length=20, null=True, blank=True)
    agresso_number = models.CharField(max_length=15, null=True, blank=True)
    social_security_number = models.CharField(max_length=25, null=True, blank=True)
    staff_full_name = models.CharField(max_length=200, null=True, blank=True)
    duty_station = models.CharField(max_length=150, null=True, blank=True)
    cost_centre = models.CharField(max_length=15, null=True, blank=True)
    job_title = models.CharField(max_length=200, null=True, blank=True)
    summary_report = models.ForeignKey(ExTraSummaryReportInfo, on_delete=models.SET_NULL, null=True, blank=True)
    earnings = models.ManyToManyField('users.PayrollProcessors')

    def total_social_security(self):
        if self.earnings is not None and self.earnings.count() > 0:
            return sum([amount[0] for amount in self.earnings.values_list('amount')])
        return 0

    def __str__(self):
        return f'Social Security - {self.staff_full_name}'


# noinspection DuplicatedCode
class TaxationReport(models.Model):
    report_id = models.CharField(max_length=50, editable=False, primary_key=True)
    period = models.CharField(max_length=20, null=True, blank=True)
    agresso_number = models.CharField(max_length=15, null=True, blank=True)
    staff_full_name = models.CharField(max_length=200, null=True, blank=True)
    cost_centre = models.CharField(max_length=15, null=True, blank=True)
    tin_number = models.CharField(max_length=30, null=True, blank=True)
    summary_report = models.ForeignKey(ExTraSummaryReportInfo, on_delete=models.SET_NULL, null=True, blank=True)
    earnings = models.ManyToManyField('users.PayrollProcessors', related_name='earnings_to_show')
    deductions = models.ManyToManyField('users.PayrollProcessors', related_name='deductions_to_show')

    def __str__(self):
        return f'PIT - {self.staff_full_name}'


# noinspection DuplicatedCode
class BankReport(models.Model):
    report_id = models.CharField(max_length=50, editable=False)
    period = models.CharField(max_length=15, null=True, blank=True)
    agresso_number = models.CharField(max_length=15, null=True, blank=True)
    staff_full_name = models.CharField(max_length=200, null=True, blank=True)
    payment_location = models.CharField(max_length=200, null=True, blank=True)
    bank = models.CharField(max_length=200, null=True, blank=True)
    branch = models.CharField(max_length=150, null=True, blank=True)
    sort_code = models.CharField(max_length=15, null=True, blank=True)
    account_number = models.CharField(max_length=30, null=True, blank=True)
    summary_report = models.ForeignKey(ExTraSummaryReportInfo, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Bank - {self.staff_full_name}'


# noinspection DuplicatedCode
class CashReport(models.Model):
    report_id = models.CharField(max_length=50, editable=False, primary_key=True)
    period = models.CharField(max_length=15, null=True, blank=True)
    agresso_number = models.CharField(max_length=15, null=True, blank=True)
    staff_full_name = models.CharField(max_length=200, null=True, blank=True)
    job_title = models.CharField(max_length=200, null=True, blank=True)
    payment_location = models.CharField(max_length=200, null=True, blank=True)
    payment_type = models.CharField(max_length=20, null=True, blank=True)
    summary_report = models.ForeignKey(ExTraSummaryReportInfo, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Cash - {self.staff_full_name}'
