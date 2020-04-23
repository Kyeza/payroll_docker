from django import forms

from .models import DutyStation


class DutyStationCreationForm(forms.ModelForm):

    class Meta:
        model = DutyStation
        fields = '__all__'


class DeclinePayrollMessageForm(forms.Form):
    approver_id = forms.IntegerField(widget=forms.HiddenInput())
    message = forms.Textarea()
