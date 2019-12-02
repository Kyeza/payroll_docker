from django import forms

from .models import PayrollPeriod, PayrollCenter


class PayrollPeriodCreationForm(forms.ModelForm):

    status = forms.CharField(initial='OPEN', disabled=True)

    class Meta:
        model = PayrollPeriod
        fields = ['payroll_center', 'month', 'year', 'status', 'processing_dollar_rate']
