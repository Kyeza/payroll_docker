from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from payroll.models import EarningDeductionType, PayrollPeriod, PayrollSummaryApprovals
from reports.helpers.mailer import Mailer
from users.models import Employee, User
from .forms import DutyStationCreationForm, DeclinePayrollMessageForm
from .models import Organization, Tax, Country, Nationality, DutyStation, Department, JobTitle, ContractType, Grade, \
    TerminationReason, PayrollApprover


class OrganizationCreate(LoginRequiredMixin, CreateView):
    model = Organization
    fields = ['name', 'country']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Organization'
        return context


class OrganizationUpdate(LoginRequiredMixin, UpdateView):
    model = Organization
    fields = ['name', 'country']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Organization'
        return context


class OrganizationDetailView(LoginRequiredMixin, DetailView):
    model = Organization
    fields = ['name', 'country']


class OrganizationListView(LoginRequiredMixin, ListView):
    model = Organization
    ordering = 'pk'


class OrganizationDelete(LoginRequiredMixin, DeleteView):
    model = Organization
    success_url = reverse_lazy('support_data:organization-list')


class TaxBracketCreate(LoginRequiredMixin, CreateView):
    model = Tax
    fields = ['country', 'lower_boundary', 'upper_boundary', 'fixed_amount', 'year']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Tax Bracket'
        return context


class TaxBracketUpdate(LoginRequiredMixin, UpdateView):
    model = Tax
    fields = ['country', 'lower_boundary', 'upper_boundary', 'fixed_amount', 'year']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Tax Bracket'
        return context


class TaxBracketDetailView(LoginRequiredMixin, DetailView):
    model = Tax
    fields = ['country', 'lower_boundary', 'upper_boundary', 'fixed_amount', 'year']


class TaxBracketListView(LoginRequiredMixin, ListView):
    model = Tax
    fields = ['country', 'lower_boundary', 'upper_boundary', 'fixed_amount', 'year']


class CountryOriginCreate(LoginRequiredMixin, CreateView):
    model = Country
    fields = ['country_name', 'country_code']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Country of Origin'
        return context


class CountryOriginUpdate(LoginRequiredMixin, UpdateView):
    model = Country
    fields = ['country_name', 'country_code']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Country of Origin'
        return context


class CountryOriginDetailView(LoginRequiredMixin, DetailView):
    model = Country
    fields = ['country_name', 'country_code']


class CountryOriginListView(LoginRequiredMixin, ListView):
    model = Country
    fields = ['country_name', 'country_code']


class NationalityCreate(LoginRequiredMixin, CreateView):
    model = Nationality
    fields = ['country', 'country_nationality']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Nationality'
        return context


class NationalityUpdate(LoginRequiredMixin, UpdateView):
    model = Nationality
    fields = ['country', 'country_nationality']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Nationality'
        return context


class NationalityDetailView(LoginRequiredMixin, DetailView):
    model = Nationality
    fields = ['country', 'country_nationality']


class NationalityListView(LoginRequiredMixin, ListView):
    model = Nationality
    fields = ['country', 'country_nationality']


class DutyStationCreate(LoginRequiredMixin, CreateView):
    model = DutyStation
    form_class = DutyStationCreationForm

    def get_initial(self):
        hardship_allowance = EarningDeductionType.objects.filter(ed_type__icontains='hardship allowance').first()
        if hardship_allowance:
            return {'earnings_type': hardship_allowance}
        else:
            return super().get_initial()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Duty Station'
        return context


class DutyStationUpdate(LoginRequiredMixin, UpdateView):
    model = DutyStation
    form_class = DutyStationCreationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Duty Station'
        return context


class DutyStationDetailView(LoginRequiredMixin, DetailView):
    model = DutyStation
    fields = ['duty_station', 'description', 'country']


class DutyStationListView(LoginRequiredMixin, ListView):
    model = DutyStation
    fields = ['duty_station', 'description', 'country']


class DepartmentCreate(LoginRequiredMixin, CreateView):
    model = Department
    fields = ['department', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Department'
        return context


class DepartmentUpdate(LoginRequiredMixin, UpdateView):
    model = Department
    fields = ['department', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Department'
        return context


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    fields = ['department', 'description']


class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    fields = ['department', 'description']


class JobTitleCreate(LoginRequiredMixin, CreateView):
    model = JobTitle
    fields = ['job_title', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Job Title'
        return context


class JobTitleUpdate(LoginRequiredMixin, UpdateView):
    model = JobTitle
    fields = ['job_title', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Job Title'
        return context


class JobTitleDetailView(LoginRequiredMixin, DetailView):
    model = JobTitle
    fields = ['job_title', 'description']


class JobTitleListView(LoginRequiredMixin, ListView):
    model = JobTitle
    fields = ['job_title', 'description']


class ContractTypeCreate(LoginRequiredMixin, CreateView):
    model = ContractType
    fields = ['contract_type', 'contract_expiry', 'leave_entitled', 'leave_days_entitled']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Contract Type'
        return context


class ContractTypeUpdate(LoginRequiredMixin, UpdateView):
    model = ContractType
    fields = ['contract_type', 'contract_expiry', 'leave_entitled', 'leave_days_entitled']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Contract Type'
        return context


class ContractTypeDetailView(LoginRequiredMixin, DetailView):
    model = ContractType
    fields = ['contract_type', 'contract_expiry', 'leave_entitled', 'leave_days_entitled']


class ContractTypeListView(LoginRequiredMixin, ListView):
    model = ContractType
    fields = ['contract_type', 'contract_expiry', 'leave_entitled', 'leave_days_entitled']


class GradeCreate(LoginRequiredMixin, CreateView):
    model = Grade
    fields = ['grade', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Grade'
        return context


class GradeUpdate(LoginRequiredMixin, UpdateView):
    model = Grade
    fields = ['grade', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Grade'
        return context


class GradeDetailView(LoginRequiredMixin, DetailView):
    model = Grade
    fields = ['grade', 'description']


class GradeListView(LoginRequiredMixin, ListView):
    model = Grade
    fields = ['grade', 'description']


class TerminationReasonCreateView(LoginRequiredMixin, CreateView):
    model = TerminationReason
    fields = ['reason']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Termination Reason'
        return context


class TerminationReasonUpdateView(LoginRequiredMixin, UpdateView):
    model = TerminationReason
    fields = ['reason']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Termination Reason'
        return context


class TerminationReasonListView(LoginRequiredMixin, ListView):
    model = TerminationReason


def send_mail_to_approvers(request, period_id):
    approvers = PayrollApprover.objects.all()
    payroll_period = PayrollPeriod.objects.get(pk=period_id)

    payroll_period.payrollprocessormanager.processed_status = 'YES'
    payroll_period.payrollprocessormanager.save()

    approvers_mails = []
    if approvers.exists():
        for approver in approvers:
            approvers_mails.append(approver.approver.email)
        mailer = Mailer(request.user.email)
        subject = f'PAYROLL APPROVAL FOR MONTH OF {payroll_period.month}'
        body = f'Please follow this link (http://127.0.0.1:8000/reports/summary_report/{period_id}) to approve the payroll summary'
        mailer.send_messages(subject, body, approvers_mails)

    messages.success(request, 'Approval request has been successfully sent')
    return redirect('reports:generate-reports')


def sign_off_payroll_summary(request, period_id):
    # noinspection PyBroadException
    approver = None
    try:
        approver = request.user.employee.id_number
    except Exception:
        pass

    payroll_period = PayrollPeriod.objects.get(pk=period_id)

    if approver:
        signature = f'{payroll_period.payroll_key}{approver}'
        PayrollSummaryApprovals.objects.create(approver_names=request.user.get_full_name(),
                                               payroll_summary=payroll_period.payroll_key,
                                               signature=signature)
    messages.success(request, f'Approved Payroll for {payroll_period.month} successfully.')
    return redirect('payroll:payroll-period-update', pk=payroll_period.id)


def decline_payroll_summary(request):
    if request.method == "POST":
        print(request.POST)


def checkout_for_approval_status(request, period_id):
    payroll_period = PayrollPeriod.objects.get(pk=period_id)
    payroll_approvers = PayrollApprover.objects.all()
    confirmatory_signatures = []
    for user in payroll_approvers.iterator():
        signature = f'{payroll_period.payroll_key}{user.approver.employee.id_number}'
        confirmatory_signatures.append(signature)

    approvals = PayrollSummaryApprovals.objects.filter(payroll_summary__exact=payroll_period.payroll_key).values_list(
        'signature')
    current_approvals_signatures = []
    for approval in approvals.iterator():
        current_approvals_signatures.append(approval[0])

    if current_approvals_signatures == confirmatory_signatures and len(confirmatory_signatures) != 0:
        return JsonResponse({'status': 'YES'})
    else:
        return JsonResponse({'status': 'NO'})
