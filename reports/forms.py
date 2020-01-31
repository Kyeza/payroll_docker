from datetime import datetime

from django import forms

from payroll.constants import PAYROLL_YEARS, MONTHS
from payroll.models import PayrollCenter, PayrollPeriod
from .models import ExTraSummaryReportInfo


class SummaryReportUpdateForm(forms.ModelForm):
    total_deductions = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={'style': 'border: none; outline: none; text-align: right;'}
        )
    )
    net_pay = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={'style': 'border: none; outline: none; text-align: right;'}
        )
    )
    gross_earning = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={'style': 'border: none; outline: none; text-align: right;'}
        )
    )

    class Meta:
        model = ExTraSummaryReportInfo
        exclude = ['key']


class ReportGeneratorForm(forms.Form):
    REPORTS = (
        ('NSSF', 'NSIF'),
        ('PAYE', 'PIT'),
        ('BANK', 'Bank'),
        ('CASH', 'Cash'),
        ('SUMMARY', 'Summary report/Pay Slip'),
        ('LEGER_EXPORT', 'Leger export')
    )
    _year = datetime.now().year
    _month = datetime.now().month
    payroll_center = forms.ModelChoiceField(queryset=PayrollCenter.objects.prefetch_related('payrollperiod_set').all(),
                                            widget=forms.Select())
    report_type = forms.ChoiceField(choices=REPORTS, widget=forms.Select())
    start_year = forms.ChoiceField(choices=PAYROLL_YEARS, widget=forms.Select(), initial=_year)
    end_year = forms.ChoiceField(choices=PAYROLL_YEARS, widget=forms.Select(), initial=_year)
    start_month = forms.ChoiceField(choices=MONTHS, widget=forms.Select(), initial=MONTHS[_month - 1][1])
    end_month = forms.ChoiceField(choices=MONTHS, widget=forms.Select(), initial=MONTHS[_month - 1][1])


class ReconciliationReportGeneratorForm(forms.Form):
    first_payroll_period = forms.ModelChoiceField(queryset=PayrollPeriod.objects.all(), widget=forms.Select())
    second_payroll_period = forms.ModelChoiceField(queryset=PayrollPeriod.objects.all(), widget=forms.Select())
