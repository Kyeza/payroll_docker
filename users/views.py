import logging
import os
import re
from builtins import super
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from payroll.models import PayrollPeriod, PayrollCenterEds, EarningDeductionType
from reports.helpers.mailer import Mailer
from reports.models import ExTraSummaryReportInfo
from support_data.models import JobTitle, SudaneseTaxRates, DutyStation, ContractType, Department, Grade
from users.mixins import NeverCacheMixin
from users.models import Employee, PayrollProcessors, CostCentre, SOF, DEA, EmployeeProject, Category, Project, \
    TerminatedEmployees, EmployeeMovement, User
from .forms import StaffCreationForm, ProfileCreationForm, StaffUpdateForm, ProfileUpdateForm, \
    EmployeeApprovalForm, TerminationForm, EmployeeProjectForm, LoginForm, ProfileGroupForm, EmployeeMovementForm, \
    EnumerationsMovementForm

logger = logging.getLogger('payroll')

path = settings.MEDIA_ROOT


def get_user_folder_name(user):
    folder_name = '/{0}_documents'.format(user.username.replace('.', '_').replace('@', ''))
    return folder_name


@never_cache
def login_admin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_active:
                login(request, user)
                return redirect('payroll/')
            else:
                messages.warning(request, 'Invalid Username or Password!')
                return render(request, 'users/auth/login.html', {'form': form})
    else:
        form = LoginForm()

    return render(request, 'users/auth/login.html', {'form': form})


def get_staff_emails_for_user_group(group_id):
    group = Group.objects.get(pk=group_id)
    staffs = group.user_set.all()
    to_emails = []
    for staff in staffs:
        to_emails.append(staff.email)
    return to_emails


@never_cache
@login_required
@permission_required(('users.add_user', 'users.add_employee'), raise_exception=True)
def register_employee(request):
    if request.method == 'POST':
        user_creation_form = StaffCreationForm(request.POST)
        profile_creation_form = ProfileCreationForm(request.POST, request.FILES)

        logging.getLogger('payroll').info(
            f'Is User post data valid: {user_creation_form.is_valid()} and is Profile post data \
            {profile_creation_form.is_valid()}')

        if user_creation_form.is_valid() and profile_creation_form.is_valid():
            user = user_creation_form.save(commit=False)
            user.save()
            user_profile = profile_creation_form.save(commit=False)
            user_profile.user = user
            user_profile.user_group = Group.objects.get(pk=6)
            user_profile.save()
            profile_creation_form.save_m2m()
            user_profile.user_group.user_set.add(user)

            emails = get_staff_emails_for_user_group(8)

            if emails:
                mailer = Mailer(settings.DEFAULT_FROM_EMAIL)
                subject = 'PAYROLL EMPLOYEE REGISTRATION NOTIFICATION'
                link = 'http://127.0.0.1:8000/users/new_employee_approval/'
                body = f'Hello All, \n\nEmployee {user.get_full_name()} has been registered to the  system. \nYou can kindly approve him/her using the following the link below:\n {link}'
                mailer.send_messages(subject, body, emails)

            logger.info(
                f"Employee: {user.get_full_name()} has been successful" +
                f"ly created. Employee data: {profile_creation_form.cleaned_data}")

            messages.success(request, 'You have successfully created a new Employee')
            return redirect('users:new-employee')
    else:
        user_creation_form = StaffCreationForm()
        profile_creation_form = ProfileCreationForm(initial={'user_group': Group.objects.get(pk=6)})

    context = {
        'title': 'New Employee',
        'user_creation_form': user_creation_form,
        'profile_creation_form': profile_creation_form,
    }
    return render(request, 'users/auth/register.html', context)


@never_cache
@login_required
@transaction.atomic
def profile(request):
    user = request.user
    try:
        employee = Employee.objects.get(pk=user.pk)
    except Employee.DoesNotExist:
        return redirect('payroll:index')

    if request.method == 'POST':
        user_update_form = StaffUpdateForm(request.POST, instance=user)
        profile_update_form = ProfileUpdateForm(request.POST, request.FILES, instance=employee)

        if user_update_form.is_valid() and profile_update_form.is_valid():
            logger.info(f'Form updated')
            user_update_form.save()
            profile_update_form.save()
            messages.success(request, 'Employee has been updated')
            return redirect('users:user-profile')
    else:
        user_update_form = StaffUpdateForm(instance=user)
        profile_update_form = ProfileUpdateForm(instance=employee)

    try:
        documents_list = os.listdir(path + get_user_folder_name(user))
    except FileNotFoundError:
        documents_list = None

    context = {
        'profile_user': user,
        'user_update_form': user_update_form,
        'profile_update_form': profile_update_form,
        'documents_list': documents_list,
        'folder_name': get_user_folder_name(user).replace('/', '').replace('/', ''),
    }
    return render(request, 'users/auth/profile.html', context)


@never_cache
@login_required
@permission_required(('users.change_user', 'users.change_employee'), raise_exception=True)
@transaction.atomic
def user_update_profile(request, pk=None):
    employee = get_object_or_404(Employee, pk=pk)
    user = employee.user

    if request.method == 'POST':
        user_update_form = StaffUpdateForm(request.POST, instance=user)
        profile_update_form = ProfileUpdateForm(request.POST, request.FILES, instance=employee)
        if user_update_form.is_valid() and profile_update_form.is_valid():
            user = user_update_form.save(commit=False)
            user.save()
            user_profile = profile_update_form.save(commit=False)
            try:
                group = Group.objects.get(pk=request.POST.get('user_group'))
                user_profile.user_group = group
            except Group.DoesNotExist:
                logger.error(f"UserUpdateView: user {user.username} doesn't belong any Group.")

            user_profile.save()
            profile_update_form.save_m2m()

            if user.groups.first():
                if user_profile.user_group:
                    if not user.groups.first() == user_profile.user_group:
                        user.groups.first().user_set.remove(user)
                        user_profile.user_group.user_set.add(user)
            else:
                if user_profile.user_group:
                    if user not in user_profile.user_group.user_set.all():
                        user_profile.user_group.user_set.add(user)

            # add user to PayrollProcessor
            add_user_to_payroll_processor(user)

            messages.success(request, 'Employee has been updated')
            return redirect('users:edit-employee')
    else:
        user_update_form = StaffUpdateForm(instance=user)
        profile_update_form = ProfileUpdateForm(instance=employee, initial={'user_group': employee.user_group})

    try:
        documents_list = os.listdir(path + get_user_folder_name(user))
    except FileNotFoundError:
        documents_list = None

    context = {
        'profile_user': user,
        'user_update_form': user_update_form,
        'profile_update_form': profile_update_form,
        'documents_list': documents_list,
        'folder_name': get_user_folder_name(user).replace('/', ''),
    }
    return render(request, 'users/auth/profile.html', context)


@never_cache
@login_required
@permission_required('users.can_change_user_group', raise_exception=True)
@transaction.atomic
def user_change_group(request, pk=None):
    employee = get_object_or_404(Employee, pk=pk)
    user = employee.user

    if request.method == 'POST':
        user_update_form = StaffUpdateForm(request.POST, instance=user)
        profile_update_form = ProfileGroupForm(request.POST, request.FILES, instance=employee)

        if user_update_form.is_valid() and profile_update_form.is_valid():
            user = user_update_form.save(commit=False)
            user.save()
            user_profile = profile_update_form.save(commit=False)

            group = Group.objects.get(pk=request.POST.get('user_group'))
            user_profile.user_group = group

            user_profile.save()

            current_user_group = user.groups.first()

            if current_user_group is not None:
                if user_profile.user_group:
                    if not user.groups.first() == user_profile.user_group:
                        user.groups.first().user_set.remove(user)
                        user_profile.user_group.user_set.add(user)
            else:
                if user_profile.user_group:
                    if user not in user_profile.user_group.user_set.all():
                        user_profile.user_group.user_set.add(user)

            logger.info(f'Employee {user.get_full_name()} has been add to user group {group}')
            messages.success(request, 'Employee\'s User group has been changed successfully')
            return redirect('payroll:index')
    else:
        user_update_form = StaffUpdateForm(instance=user)
        profile_update_form = ProfileGroupForm(instance=employee)

    context = {
        'profile_user': user,
        'user_update_form': user_update_form,
        'profile_update_form': profile_update_form,
    }
    return render(request, 'users/auth/change_user_group_form.html', context)


def add_users_for_period(payroll_period, instance):
    logger.debug(f'Adding user to Period {payroll_period}')
    user_payroll_center = instance.employee.payroll_center
    payroll_center_ed_types = PayrollCenterEds.objects.select_related('ed_type') \
        .filter(payroll_center=user_payroll_center)

    if payroll_center_ed_types.exists():
        # get existing instance processors if they exists
        existing_user_payroll_processors = PayrollProcessors.objects \
            .select_related('employee', 'earning_and_deductions_type', 'earning_and_deductions_category',
                            'payroll_period', 'earning_and_deductions_type__ed_category_id',
                            'earning_and_deductions_type__ed_type') \
            .filter(employee=instance.employee).filter(payroll_period=payroll_period)
        # if ed_types for the employees payroll center exist
        if existing_user_payroll_processors.exists():
            logger.debug(f'user\'s {payroll_period} processors exist')
            # PayrollCenterEdTypes can change, hence in case there is one not in the processor
            # associated with that instance, then create it
            for pc_ed_type in payroll_center_ed_types.iterator():
                ed_type = existing_user_payroll_processors.filter(earning_and_deductions_type=pc_ed_type.ed_type)
                if ed_type.exists():
                    # if that ed_type already has a processor associated with the instance leave
                    # it and continue
                    continue
                else:
                    # else create it
                    logger.debug(f'adding {pc_ed_type.ed_type.ed_type} to user\'s existing processors')
                    user_process = PayrollProcessors(employee=instance.employee,
                                                     earning_and_deductions_category=pc_ed_type
                                                     .ed_type.ed_category,
                                                     earning_and_deductions_type=pc_ed_type.ed_type,
                                                     amount=0, payroll_period=payroll_period)
                    user_process.save()

        else:
            logger.debug(f'Creating user\'s {payroll_period} processes in Processor')
            # if its a new instance in the payroll period, create processors for that
            # instance/employee
            for pc_ed_type in payroll_center_ed_types.iterator():
                basic_salary_reg = re.compile(r'basic salary', re.IGNORECASE, )
                hardship_allowance_reg = re.compile(r'hardship allowance', re.IGNORECASE, )
                user_process = None
                if pc_ed_type.ed_type.id == 1:
                    user_process = PayrollProcessors(employee=instance.employee,
                                                     earning_and_deductions_category=pc_ed_type
                                                     .ed_type.ed_category,
                                                     earning_and_deductions_type=pc_ed_type.ed_type,
                                                     amount=instance.employee.basic_salary,
                                                     payroll_period=payroll_period)
                    logger.info(
                        f'Added {instance} {pc_ed_type.ed_type.ed_type} earning to period processes')
                elif pc_ed_type.ed_type.id == 2:
                    if instance.employee.duty_station:
                        user_process = PayrollProcessors(employee=instance.employee,
                                                         earning_and_deductions_category=pc_ed_type
                                                         .ed_type.ed_category,
                                                         earning_and_deductions_type=pc_ed_type.ed_type,
                                                         amount=instance.employee.duty_station
                                                         .earning_amount,
                                                         payroll_period=payroll_period)
                        logger.info(
                            f'Added {instance} {pc_ed_type.ed_type.ed_type} earning to period processes')
                elif pc_ed_type.ed_type.id == 78:
                    user_process = PayrollProcessors(employee=instance.employee,
                                                     earning_and_deductions_category=pc_ed_type
                                                     .ed_type.ed_category,
                                                     earning_and_deductions_type=pc_ed_type.ed_type,
                                                     amount=22,
                                                     payroll_period=payroll_period)
                    logger.info(
                        f'Added {instance} {pc_ed_type.ed_type.ed_type} earning to period processes')
                else:
                    user_process = PayrollProcessors(employee=instance.employee,
                                                     earning_and_deductions_category=pc_ed_type
                                                     .ed_type.ed_category,
                                                     earning_and_deductions_type=pc_ed_type.ed_type,
                                                     amount=0,
                                                     payroll_period=payroll_period)
                    logger.info(
                        f'Added {instance} {pc_ed_type.ed_type.ed_type} earning to period processes')

                if user_process:
                    user_process.save()
                else:
                    logger.error(
                        f'PayrollCenter {pc_ed_type.ed_type.ed_type} for {instance} was not processed')
    else:
        logger.error(f'Payroll center has no Earnings and Deductions')


def add_user_to_payroll_processor(instance, payroll_period=None):
    logger.debug(f'adding user: {instance} to payroll processor')
    user_status = instance.employee.employment_status
    if payroll_period:
        add_users_for_period(payroll_period, instance)
    else:
        payroll_periods = instance.employee.payroll_center.payrollperiod_set.all()
        if user_status == 'APPROVED' or user_status == 'REACTIVATED':
            if payroll_periods.exists():
                open_payroll_period = payroll_periods.filter(status='OPEN').all()
                if open_payroll_period.exists():
                    for payroll_period in open_payroll_period:
                        add_users_for_period(payroll_period, instance)
                else:
                    logger.error(f'No OPEN payroll periods in the Processor')
            else:
                logger.error(f'No PayrollPeriods in the Processor')
        else:
            logger.error(f'{instance} either not APPROVED or REACTIVATED')


@login_required
@permission_required('users.approve_employee', raise_exception=True)
def reject_employee(request, pk=None):
    employee = get_object_or_404(Employee, pk=pk)
    employee.employment_status = 'REJECTED'
    employee.save(update_fields=['employment_status'])
    return render(request, 'users/employees/_approved_employee_list.html')


@login_required
@permission_required('users.approve_employee', raise_exception=True)
@transaction.atomic
def approve_employee(request, pk=None):
    employee = get_object_or_404(Employee, pk=pk)
    profile_user = employee.user

    if request.method == 'POST':
        user_update_form = StaffUpdateForm(request.POST, instance=profile_user)
        profile_update_form = EmployeeApprovalForm(request.POST, request.FILES, instance=employee)
        if user_update_form.is_valid() and profile_update_form.is_valid():
            user = user_update_form.save()
            employee_profile = profile_update_form.save(commit=False)

            # change employee status to approved before saving to db and adding them to payroll processors
            employee_profile.employment_status = 'APPROVED'
            employee_profile.save()
            profile_update_form.save_m2m()

            # add user to PayrollProcessor
            add_user_to_payroll_processor(profile_user)

            # logger.info(f'{request.user} approved Employee {employee_profile.user}')

            emails = get_staff_emails_for_user_group(8)

            if emails:
                mailer = Mailer(settings.DEFAULT_FROM_EMAIL)
                subject = 'PAYROLL EMPLOYEE APPROVAL NOTIFICATION'
                body = f'Hello All, \n\nEmployee {user.get_full_name()} has been approved.'
                mailer.send_messages(subject, body, emails)

            messages.success(request, f'{employee} has been approved')
            return redirect('users:employee-approval')
    else:
        user_update_form = StaffUpdateForm(instance=profile_user)
        profile_update_form = EmployeeApprovalForm(instance=employee)

    try:
        documents_list = os.listdir(path + get_user_folder_name(profile_user))
    except FileNotFoundError:
        documents_list = None

    context = {
        'profile_user': profile_user,
        'user_update_form': user_update_form,
        'profile_update_form': profile_update_form,
        'documents_list': documents_list,
        'folder_name': get_user_folder_name(profile_user).replace('/', '').replace('/', ''),
    }
    return render(request, 'users/employees/_approve_employee.html', context)


class RecruitedEmployeeListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ('users.approve_employee',)
    model = Employee
    template_name = 'users/employees/_recruited_employee_list.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Employee.objects.select_related('user', 'department', 'job_title') \
                .filter(employment_status='Recruit').order_by('-appointment_date').iterator()
        else:
            assigned_user_locations = list(self.request.user.employee.assigned_locations.all())
            return Employee.objects.select_related('user', 'department', 'job_title') \
                .filter(employment_status='Recruit').order_by('-appointment_date')\
                .filter(duty_station__in=assigned_user_locations).iterator().iterator()


class ApprovedEmployeeListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ('users.change_user', 'users.change_employee')
    model = Employee

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Employee.objects.prefetch_related('assigned_locations') \
                .select_related('user', 'nationality', 'grade', 'duty_station', 'duty_country', 'department',
                                'job_title', 'line_manager', 'contract_type', 'payroll_center', 'bank_1', 'bank_2',
                                'category', 'currency', 'kin_relationship', 'district') \
                .filter(employment_status='Approved').iterator()
        else:
            assigned_user_locations = list(self.request.user.employee.assigned_locations.all())
            return Employee.objects.prefetch_related('assigned_locations') \
                .select_related('user', 'nationality', 'grade', 'duty_station', 'duty_country', 'department',
                                'job_title', 'line_manager', 'contract_type', 'payroll_center', 'bank_1', 'bank_2',
                                'category', 'currency', 'kin_relationship', 'district') \
                .filter(employment_status='Approved').filter(duty_station__in=assigned_user_locations).iterator()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['title'] = 'Staff'
        return context


class ChangeGroupEmployeeListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ('users.can_change_user_group',)
    model = Employee
    template_name = 'users/employees/change_group_employee_list.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Employee.objects \
                .select_related('user', 'nationality', 'grade', 'duty_station', 'duty_country', 'department', 'job_title',
                                'line_manager', 'contract_type', 'payroll_center', 'bank_1', 'bank_2', 'category',
                                'currency', 'kin_relationship', 'district') \
                .filter(employment_status='Approved').iterator()
        else:
            assigned_user_locations = list(self.request.user.employee.assigned_locations.all())
            return Employee.objects \
                .select_related('user', 'nationality', 'grade', 'duty_station', 'duty_country', 'department',
                                'job_title',
                                'line_manager', 'contract_type', 'payroll_center', 'bank_1', 'bank_2', 'category',
                                'currency', 'kin_relationship', 'district') \
                .filter(employment_status='Approved').filter(duty_station__in=assigned_user_locations).iterator().iterator()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['title'] = 'Staff'
        return context


class RejectedEmployeeListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ('users.view_user', 'users.view_employee')
    model = Employee
    template_name = 'users/employees/_rejected_employee_list.html'

    def get_queryset(self):
        return Employee.objects.select_related('user', 'department', 'job_title') \
            .filter(employment_status='REJECTED').iterator()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['title'] = 'Rejected Staff'
        return context


class SeparatedEmployeesListView(LoginRequiredMixin, NeverCacheMixin, PermissionRequiredMixin, ListView):
    permission_required = ('users.view_user', 'users.view_employee')
    model = Employee
    template_name = 'users/employees/_separated_employee_list.html'

    def get_queryset(self):
        return Employee.objects \
            .select_related('user', 'department', 'job_title').filter(employment_status='Terminated') \
            .order_by('-appointment_date').iterator()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['title'] = 'Separated Employees'
        return context


def processor(request_user, payroll_period, process_with_rate=None, method='GET', user=None):
    logger.info(f'started payroll process processing')
    response = {}
    payroll_center = payroll_period.payroll_center
    if process_with_rate:
        payroll_period.processing_dollar_rate = process_with_rate
        try:
            payroll_period.save()
        except ValidationError:
            payroll_period.created_by = request_user
            payroll_period.save()

    users = payroll_center.employee_set.all()
    employees_in_period = set()
    if users.exists() and user is None:
        logger.critical(f'Adding Payroll center users for Period {payroll_period} to processor')
        for employee in users:
            if employee.employment_status == 'APPROVED':
                inst = employee.user
                try:
                    add_user_to_payroll_processor(inst, payroll_period)
                except Exception as e:
                    logger.error(f'Something went wrong')
                    logger.error(f'{e.args}')
        logger.critical(f'Successfully added users for Period {payroll_period} to processor')
    elif user:
        employees_in_period.add(user)
    else:
        logger.error(f'No Employees in the system')
        response['message'] = 'Something went wrong'
        response['status'] = 'Failed: No Employees in the system'

    if user:
        period_processes = PayrollProcessors.objects \
            .select_related('employee', 'earning_and_deductions_type', 'earning_and_deductions_category',
                            'employee__nationality', 'employee__grade', 'employee__duty_station',
                            'employee__duty_country',
                            'employee__department', 'employee__job_title', 'employee__line_manager',
                            'employee__contract_type', 'employee__payroll_center', 'employee__bank_1',
                            'employee__bank_2',
                            'employee__category') \
            .filter(payroll_period=payroll_period).filter(employee=user) \
            .filter(payroll_period__payroll_center_id=payroll_center.id).all() \
            .prefetch_related('employee__report', 'employee__report__payroll_period')
        logger.debug(f'Processors: {period_processes.count()}')
    else:
        period_processes = PayrollProcessors.objects \
            .select_related('employee', 'earning_and_deductions_type', 'earning_and_deductions_category',
                            'employee__nationality', 'employee__grade', 'employee__duty_station',
                            'employee__duty_country',
                            'employee__department', 'employee__job_title', 'employee__line_manager',
                            'employee__contract_type', 'employee__payroll_center', 'employee__bank_1',
                            'employee__bank_2',
                            'employee__category') \
            .filter(payroll_period=payroll_period).filter(payroll_period__payroll_center_id=payroll_center.id).all() \
            .prefetch_related('employee__report', 'employee__report__payroll_period')

    # removing any terminated employees before processing
    if users.exists() and user is None:
        if period_processes.exists():
            for process in period_processes.iterator():
                if process.employee.employment_status == 'TERMINATED':
                    process.delete()
                else:
                    employees_in_period.add(process.employee)
        else:
            logger.error(f'Here - > There are currently no Employees for this Payroll Period')
            response['message'] = 'There are currently no Employees for this Payroll Period'
            response['status'] = 'Failed: There are currently no Employees for this Payroll Period'
    elif len(employees_in_period) == 0:
        logger.error(f'No Employees in the system')

    logger.info(f'Calculating tax rates according to current dollar rate ({process_with_rate})')
    current_tax_rates = SudaneseTaxRates.objects.all()
    if current_tax_rates.exists():
        for i, tax_bracket in enumerate(current_tax_rates):
            if i < 2:
                tax_bracket.actual_usd = round(tax_bracket.upper_ssp_bound / Decimal(process_with_rate))
            if i == 1:
                tax_bracket.actual_usd_taxable_amount = round(Decimal(tax_bracket.tax_rate) * tax_bracket.actual_usd)
            tax_bracket.save()
    nhif_ed_type = EarningDeductionType.objects.get(pk=32)
    nhif_ed_type_17 = EarningDeductionType.objects.get(pk=31)
    accrued_ap = EarningDeductionType.objects.get(pk=72)
    accrued_gl = EarningDeductionType.objects.get(pk=73)
    for employee in employees_in_period:
        logger.info(f'Processing for user {employee}')
        basic_salary = 0
        gross_earnings, total_deductions, pit, net_pay, nhif_8, nhif_17 = 0, 0, 0, 0, 0, 0
        ge_data = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_category_id=1).all()

        # calculating gross earnings
        logger.info(f'Processing for user {employee}: calculating gross earnings')
        if ge_data.exists():
            for inst in ge_data.iterator():
                if inst.earning_and_deductions_type.id == 1 and inst.amount == 0 and user is None:
                    inst.amount = employee.basic_salary
                    inst.save(update_fields=['amount'])
                elif inst.earning_and_deductions_type.id == 2 and user is None:
                    if employee.duty_station and (
                            employee.duty_station.earning_amount is not None) and inst.amount != employee.duty_station.earning_amount:
                        inst.amount = employee.duty_station.earning_amount
                        inst.save(update_fields=['amount'])
                gross_earnings += inst.amount

        basic_salary = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=1).first().amount

        # calculating NHIF
        logger.info(f'Processing for user {employee}: calculating NHIF')
        employee_nhif = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=32).first()
        if employee_nhif:
            employee_nhif.amount = round(basic_salary * Decimal(nhif_ed_type.factor))
            nhif_8 = employee_nhif.amount
            employee_nhif.save(update_fields=['amount'])

        # calculating Taxable gross earnings
        taxable_gross_earnings = gross_earnings - employee_nhif.amount

        # calculating PIT
        logger.info(f'Processing for user {employee}: calculating PIT')

        rates = []
        for rate in current_tax_rates.iterator():
            rates.append(rate)

        if taxable_gross_earnings < rates[0].actual_usd:
            pit = 0
        else:
            tax = taxable_gross_earnings - rates[0].actual_usd
            amount = tax - rates[1].actual_usd
            if amount > rates[1].actual_usd:
                amount = amount * Decimal(rates[2].tax_rate)
            pit = amount + rates[1].actual_usd_taxable_amount

        # update PIT if exists in payroll center
        logger.info(f'Processing for user {employee}: updating PIT')
        employee_pit_processor = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=61).first()
        if employee_pit_processor:
            employee_pit_processor.amount = pit
            employee_pit_processor.save(update_fields=['amount'])

        # update Pension if exists in payroll center
        logger.info(f'Processing for user {employee}: updating Pension')
        employee_pension_processor = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=75).first()
        if employee_pension_processor:
            employee_pension_processor.amount = basic_salary * Decimal(5 / 100)
            employee_pension_processor.save(update_fields=['amount'])

        # update Employer Pension if exists in payroll center
        logger.info(f'Processing for user {employee}: updating Employer Pension')
        employer_pension = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=76).first()
        arrears = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=11).first()
        if employer_pension:
            employer_pension.amount = (basic_salary + arrears.amount) / Decimal(12)
            employer_pension.save(update_fields=['amount'])

        # update NSSF 17% if exists in payroll center
        logger.info(f'Processing for user {employee}: updating NHIF 17%')
        employee_nhif_17_processor = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=31).first()
        if employee_nhif_17_processor:
            employee_nhif_17_processor.amount = gross_earnings * Decimal(nhif_ed_type_17.factor)
            nhif_17 = employee_nhif_17_processor.amount
            employee_nhif_17_processor.save(update_fields=['amount'])

        tx_data_ded = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_category_id=2).all()
        tx_data_stat = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_category_id=3).all()

        # calculating total deductions from deductions
        logger.info(f'Processing for user {employee}: calculating total deductions from deductions')
        if tx_data_ded.exists():
            for inst in tx_data_ded.iterator():
                total_deductions += inst.amount

        # calculating total deductions from statutory deductions
        logger.info(f'Processing for user {employee}: calculating total deductions from statutory deductions')
        if tx_data_stat.exists():
            for inst in tx_data_stat.iterator():
                total_deductions += inst.amount

        logger.info(f'Processing for user {employee}: calculating NET PAY')
        net_pay = gross_earnings - total_deductions

        # update net_pay if exists in payroll center
        logger.info(f'Processing for user {employee}: Net pay')
        employee_net_pay = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=60).first()
        if employee_net_pay:
            employee_net_pay.amount = net_pay
            employee_net_pay.save(update_fields=['amount'])

        # update accrued salary ap if exists in payroll center
        logger.info(f'Processing for user {employee}: Accrued Salary AP')
        employee_accrued_salary_ap = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=72).first()
        if employee_accrued_salary_ap:
            employee_accrued_salary_ap.amount = (basic_salary + arrears.amount) / Decimal(accrued_ap.factor)
            employee_accrued_salary_ap.save(update_fields=['amount'])

        # update accrued salary gl if exists in payroll center
        logger.info(f'Processing for user {employee}: Accrued Salary AL')
        employee_accrued_salary_gl = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=73).first()
        if employee_accrued_salary_gl:
            employee_accrued_salary_gl.amount = (basic_salary + arrears.amount) / Decimal(accrued_gl.factor)
            employee_accrued_salary_gl.save(update_fields=['amount'])

        # updating NHIF export
        logger.info(f'Processing for user {employee}: NHIF Export')
        employee_nhif_export = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=77).first()
        if employee_nhif_export:
            employee_nhif_export.amount = nhif_8 + nhif_17
            employee_nhif_export.save(update_fields=['amount'])

        # updating number of working hours
        logger.info(f'Processing for user {employee}: Number of Working days')
        working_days = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=78).first()

        if working_days.amount == 0:
            working_days.amount = 22
            working_days.save()

        try:
            key = f'{payroll_period.payroll_key}S{employee.pk}'
            report = ExTraSummaryReportInfo.objects.get(pk=key)
            report.employee_name = employee.user.get_full_name()
            report.analysis = employee.agresso_number
            report.job_title = employee.job_title
            report.employee_id = employee.pk
            report.net_pay = net_pay
            report.gross_earning = gross_earnings
            report.total_deductions = total_deductions
            report.save()

            response['message'] = f'Successfully process Payroll Period with dollar rate of {process_with_rate}'
            response['status'] = 'Success'
            logger.info(f'Successfully processed {employee} Payroll Period')

        except ExTraSummaryReportInfo.DoesNotExist:
            report = ExTraSummaryReportInfo(analysis=employee.agresso_number,
                                            employee_id=employee.pk,
                                            employee_name=employee.user.get_full_name(),
                                            job_title=employee.job_title,
                                            payroll_period=payroll_period,
                                            net_pay=net_pay,
                                            gross_earning=gross_earnings,
                                            total_deductions=total_deductions)
            report.save()

            response['message'] = f'Successfully process Payroll Period with dollar rate of {process_with_rate}'
            response['status'] = 'Success'
            logger.info(f'Successfully processed {employee} Payroll Period')

    logger.info(f'Finished processing {response}')

    if method == 'POST':
        logger.debug(f'Displaying report {response}')
        return response


@login_required
@transaction.atomic()
@cache_page(60 * 15)
@permission_required('payroll.process_payrollperiod', raise_exception=True)
def process_payroll_period(request, pk, user=None):
    if request.method == 'POST' and request.is_ajax():
        logger.info(f'Starting whole processing process')
        payroll_period = get_object_or_404(PayrollPeriod, pk=pk)
        process_with_rate = float(request.POST.get('process_with_rate'))
        try:
            response = processor(request.user, payroll_period, process_with_rate, 'POST')
        except Exception as e:
            # msgs = messages.info(request, 'There are no PayrollCenter Earning and Deductions in the System')
            # html = render_to_string('partials/messages.html', {'msgs': msgs})
            logger.error(f'Something went wrong {e.args}')
            response = {'status': f'Failed: {e.args}', 'message': ''}
            return JsonResponse(response)
        else:
            return JsonResponse(response)

    elif request.method == 'GET':
        employee = Employee.objects.get(pk=user)
        payroll_period = get_object_or_404(PayrollPeriod, pk=pk)
        processor(request.user, payroll_period, process_with_rate=payroll_period.processing_dollar_rate, user=employee)
        # return HttpResponseRedirect(reverse('reports:display-summary-report', args=(payroll_period.id,)))
        return redirect('reports:display-summary-report', payroll_period.id)


@login_required
@permission_required('users.terminate_employee', raise_exception=True)
def terminate_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        form = TerminationForm(request.POST)
        if form.is_valid():
            employee.employment_status = 'TERMINATED'
            employee.save(update_fields=['employment_status'])
            instance = form.save(commit=False)
            instance.employee = employee
            instance.save()
            messages.success(request, 'Employee terminated successfully')
            return redirect('users:terminate-employee-list')
    else:
        form = TerminationForm(initial={'employee': employee})

    context = {
        'employee': employee,
        'form': form,
    }
    return render(request, 'users/employees/_terminate_employee_form.html', context)


@never_cache
@login_required
@permission_required('users.approve_employee', raise_exception=True)
def reactivate_employee(request, pk):
    user_profile = get_object_or_404(Employee, pk=pk)
    termination_form = TerminatedEmployees.objects.filter(employee=user_profile).first()
    if termination_form:
        termination_form.delete()
    user_profile.employment_status = 'RECRUIT'
    user_profile.save()
    messages.success(request, 'Employee successfully reactivated')
    return redirect('users:separated-employee')


class EmployeeBirthdayList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ('users.view_user', 'users.view_employee')
    model = Employee
    template_name = 'users/employees/_employee_birthday_list.html'

    def get_queryset(self):
        return Employee.objects.select_related('user') \
            .filter(employment_status='APPROVED').iterator()


class AssignProjectListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ('users.view_user', 'users.view_employee')
    model = Employee
    template_name = 'users/employees/_assign_employee_project_list.html'

    def get_queryset(self):
        return Employee.objects.select_related('user', 'department', 'job_title') \
            .filter(employment_status='Approved').iterator()


@login_required
@permission_required('users.assign_employee', raise_exception=True)
def create_employee_project(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        form = EmployeeProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Successfully assigned project to {employee.user.get_full_name()}')
            return redirect('users:employee-assign-project')
    else:
        form = EmployeeProjectForm(initial={'employee': employee})

    context = {
        'title': 'Assign Project',
        'form': form
    }

    return render(request, 'users/employeeproject/employeeproject_form.html', context)


class EmployeeProjectCreation(CreateView):
    model = EmployeeProject
    fields = ['employee', 'cost_center', 'project_code', 'sof_code', 'dea_code', 'contribution_percentage']
    template_name = 'users/employeeproject/employeeproject_form.html'

    def get_initial(self):
        context = super().get_initial()
        employee = Employee.objects.get(pk=self.kwargs.get('pk'))
        context['employee'] = employee
        return context

    def form_valid(self, form):
        project = form.save(commit=False)
        employee = Employee.objects.get(pk=self.kwargs.get('pk'))
        project.employee = employee
        project.save()
        messages.success(self.request, f'Successfully assigned project to {employee.user.get_full_name()}')
        return redirect('users:employee-assign-project')


class CostCentreCreate(LoginRequiredMixin, CreateView):
    model = CostCentre
    fields = ['cost_centre', 'description']
    template_name = 'users/costcentre/costcentre_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Cost Centre'
        return context


class CostCentreUpdate(LoginRequiredMixin, UpdateView):
    model = CostCentre
    fields = ['cost_centre', 'description']
    template_name = 'users/costcentre/costcentre_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Cost Centre'
        return context


class CostCentreDetailView(LoginRequiredMixin, DetailView):
    model = CostCentre
    template_name = 'users/costcentre/costcentre_detail.html'


class CostCentreListView(LoginRequiredMixin, ListView):
    model = CostCentre
    template_name = 'users/costcentre/costcentre_list.html'


class ProjectCreate(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['project_code', 'project_name']
    template_name = 'users/project/project_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Project'
        return context


class ProjectUpdate(LoginRequiredMixin, UpdateView):
    model = Project
    fields = ['project_code', 'project_name']
    template_name = 'users/project/project_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Project'
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    fields = ['project_code', 'project_name']
    template_name = 'users/project/project_detail.html'


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'users/project/project_list.html'


class SOFCreate(LoginRequiredMixin, CreateView):
    model = SOF
    fields = ['sof_code', 'sof_name']
    template_name = 'users/sof/sof_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create SOF'
        return context


class SOFUpdate(LoginRequiredMixin, UpdateView):
    model = SOF
    fields = ['sof_code', 'sof_name']
    template_name = 'users/sof/sof_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit SOF'
        return context


class SOFDetailView(LoginRequiredMixin, DetailView):
    model = SOF
    fields = ['sof_code', 'sof_name']
    template_name = 'users/sof/sof_detail.html'


class SOFListView(LoginRequiredMixin, ListView):
    model = SOF
    template_name = 'users/sof/sof_list.html'


class DEACreate(LoginRequiredMixin, CreateView):
    model = DEA
    fields = ['dea_code', 'dea_name']
    template_name = 'users/dea/dea_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create DEA'
        return context


class DEAUpdate(LoginRequiredMixin, UpdateView):
    model = DEA
    fields = ['dea_code', 'dea_name']
    template_name = 'users/dea/dea_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit DEA'
        return context


class DEADetailView(LoginRequiredMixin, DetailView):
    model = DEA
    fields = ['dea_code', 'dea_name']
    template_name = 'users/dea/dea_detail.html'


class DEAListView(LoginRequiredMixin, ListView):
    model = DEA
    template_name = 'users/dea/dea_list.html'


class EmployeeProjectsDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeProject
    fields = ['employee', 'cost_centre', 'project_code', 'sof_code', 'dea_code']
    template_name = 'users/employeeproject/employeeproject_detail.html'


class EmployeeProjectsListView(LoginRequiredMixin, ListView):
    model = EmployeeProject
    template_name = 'users/employeeproject/employeeproject_list.html'


class CategoryCreateView(CreateView):
    model = Category
    fields = ['name']
    template_name = 'users/category/category_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Category'
        return context


class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['name']
    template_name = 'users/category/category_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Category'
        return context


class CategoryDetailView(DetailView):
    model = Category
    fields = ['name']
    template_name = 'users/category/category_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Category'
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'users/category/category_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Categories'
        return context


class ApprovedEmployeeMovementsListView(ListView):
    model = Employee
    template_name = 'users/employees/employee_movements_listview.html'

    def get_queryset(self):
        return Employee.objects.select_related('user', 'nationality', 'grade', 'duty_station', 'duty_country',
                                               'department', 'job_title', 'line_manager', 'contract_type',
                                               'payroll_center',
                                               'bank_1', 'bank_2', 'category', 'currency', 'kin_relationship',
                                               'district').filter(employment_status='Approved').iterator()


class EnumEmployeeMovementsListView(ListView):
    model = Employee
    template_name = 'users/employees/employee_movements_listview_enum.html'

    def get_queryset(self):
        return Employee.objects.select_related('user', 'nationality', 'grade', 'duty_station', 'duty_country',
                                               'department', 'job_title', 'line_manager', 'contract_type',
                                               'payroll_center',
                                               'bank_1', 'bank_2', 'category', 'currency', 'kin_relationship',
                                               'district').filter(employment_status='Approved').iterator()


class EmployeeMovementsListView(ListView):
    model = EmployeeMovement

    def get_queryset(self):
        data = EmployeeMovement.objects.filter(status__exact='SHOW').prefetch_related('employee__user')
        return data


class EmployeeMovementsCreate(CreateView):
    model = EmployeeMovement
    form_class = EmployeeMovementForm

    def get_initial(self):
        data = super().get_initial()
        employee = Employee.objects.get(pk=self.kwargs.get('user_id'))
        data['employee'] = employee
        data['employee_name'] = employee.user.get_full_name()
        data['department'] = employee.department.department
        data['job_title'] = employee.job_title.job_title
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.kwargs.get('user_id')
        return context

    def form_valid(self, form):
        form_data = form.save(commit=False)
        form_data.employee = Employee.objects.get(pk=self.kwargs.get('user_id'))
        form_data.movement_requester = User.objects.get(pk=self.kwargs.get('requester_id'))
        form_data.save()

        staff_emails = get_staff_emails_for_user_group(8)

        if staff_emails:
            mailer = Mailer(settings.DEFAULT_FROM_EMAIL)
            subject = 'PAYROLL EMPLOYEE MOVEMENT NOTIFICATION'
            link = 'http://127.0.0.1:8000/users/employee/movements/'
            body = f'There are movements on the system the kindly require your approval.\n Please follow the link below: {link}'
            mailer.send_messages(subject, body, staff_emails)

        return redirect('users:employee_movements', permanent=True)


class EmployeeMovementsUpdate(UpdateView):
    model = EmployeeMovement
    form_class = EmployeeMovementForm


def load_current_param(request):
    parameter_id = int(request.GET.get('parameter'))
    user_id = int(request.GET.get('user_id'))
    user = Employee.objects.get(pk=user_id)
    movements_from = None
    if parameter_id == 1:
        movements_from = user.job_title.job_title
    elif parameter_id == 2:
        movements_from = user.duty_station.duty_station
    elif parameter_id == 3:
        movements_from = user.contract_expiry.strftime('%Y-%m-%d')
    elif parameter_id == 4:
        movements_from = user.contract_type.contract_type
    elif parameter_id == 5:
        movements_from = user.department.department
    elif parameter_id == 6:
        movements_from = user.grade.grade
    elif parameter_id == 7:
        movements_from = user.basic_salary

    context = {
        'movements_from': movements_from,
        'parameter_id': parameter_id
    }

    return JsonResponse(context)


def load_movements(request):
    parameter_id = int(request.GET.get('parameter'))
    movements_to = []
    if parameter_id == 1:
        for m in JobTitle.objects.iterator():
            movements_to.append(m.job_title)
    elif parameter_id == 2:
        for m in DutyStation.objects.iterator():
            movements_to.append(m.duty_station)
    elif parameter_id == 4:
        for m in ContractType.objects.iterator():
            movements_to.append(m.contract_type)
    elif parameter_id == 5:
        for m in Department.objects.iterator():
            movements_to.append(m.department)
    elif parameter_id == 6:
        for m in Grade.objects.iterator():
            movements_to.append(m.grade)

    context = {
        'movements_to': movements_to,
        'parameter_id': parameter_id
    }

    return render(request, 'users/movements_dropdown_list_options.html', context)


def load_earnings_current_amount(request):
    parameter_id = int(request.GET.get('parameter'))
    user_id = int(request.GET.get('user_id'))

    employee = Employee.objects.get(pk=user_id)
    period_id = int(request.GET.get('period'))
    overtime_type = request.GET.get('overtime')
    response = {}

    payroll_period = PayrollPeriod.objects.get(pk=period_id)
    period_processors = PayrollProcessors.objects.filter(payroll_period_id=payroll_period.id)
    employee_period_processors = period_processors.filter(employee_id=employee.pk)
    if employee_period_processors:
        if parameter_id == 78:
            response = employee_period_processors.filter(earning_and_deductions_type_id=1).values(
                'amount').first()
            working_days = employee_period_processors.filter(earning_and_deductions_type_id=78).values(
                'amount').first()
            response['working_days'] = working_days['amount']
        else:
            response = employee_period_processors.filter(earning_and_deductions_type_id=parameter_id).values(
                'amount').first()

    return JsonResponse(response)


class EnumerationsMovementsCreate(CreateView):
    model = EmployeeMovement
    form_class = EnumerationsMovementForm
    template_name = 'users/employeemovement_earnings_form_enums.html'

    def get_initial(self):
        data = super().get_initial()
        employee = Employee.objects.get(pk=self.kwargs.get('user_id'))
        data['employee'] = employee
        data['employee_name'] = employee.user.get_full_name()
        data['department'] = employee.department.department
        data['job_title'] = employee.job_title.job_title
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.kwargs.get('user_id')
        return context

    def form_valid(self, form):
        form_data = form.save(commit=False)
        form_data.employee = Employee.objects.get(pk=self.kwargs.get('user_id'))
        form_data.movement_requester = User.objects.get(pk=self.kwargs.get('requester_id'))
        form_data.save()

        staff_emails = get_staff_emails_for_user_group(8)

        if staff_emails:
            mailer = Mailer(settings.DEFAULT_FROM_EMAIL)
            subject = 'PAYROLL EMPLOYEE MOVEMENT NOTIFICATION'
            link = 'http://127.0.0.1:8000/users/employee/movements/'
            body = f'There are movements on the system the kindly require your approval.\n Please follow the link below: {link}'
            mailer.send_messages(subject, body, staff_emails)

        return redirect('users:employee_movements_enums', permanent=True)


def approve_employee_movement(request, movement_id):
    movement = EmployeeMovement.objects.filter(pk=movement_id).prefetch_related('employee', 'earnings').first()
    movement_name = f'{movement.earnings.ed_type.capitalize() + ", " if movement.earnings else ""}{movement}'
    employee = movement.employee

    if movement.parameter.id == 1:
        new_job_title = JobTitle.objects.filter(job_title__exact=movement.move_to).first()
        employee.job_title = new_job_title
        employee.save(update_fields=['job_title'])
        movement.status = 'APPROVED'
        movement.save(update_fields=['status'])
    elif movement.parameter.id == 2:
        new_duty_station = DutyStation.objects.filter(duty_station__exact=movement.move_to).first()
        employee.duty_station = new_duty_station
        employee.save(update_fields=['duty_station'])
        movement.status = 'APPROVED'
        movement.save(update_fields=['status'])
    elif movement.parameter.id == 3:
        # TODO: work on contract extensions
        movement.status = 'APPROVED'
        movement.save(update_fields=['status'])
    elif movement.parameter.id == 4:
        new_contract_type = ContractType.objects.filter(contract_type__exact=movement.move_to).first()
        employee.contract_type = new_contract_type
        employee.save(update_fields=['contract_type'])
        movement.status = 'APPROVED'
        movement.save(update_fields=['status'])
    elif movement.parameter.id == 5:
        new_department = Department.objects.filter(department__exact=movement.move_to).first()
        employee.department = new_department
        employee.save(update_fields=['department'])
        movement.status = 'APPROVED'
        movement.save(update_fields=['status'])
    elif movement.parameter.id == 6:
        new_grade = Grade.objects.filter(grade__exact=movement.move_to).first()
        employee.grade = new_grade
        employee.save(update_fields=['grade'])
        movement.status = 'APPROVED'
        movement.save(update_fields=['status'])
    elif movement.parameter.id == 7:
        employee.basic_salary = Decimal(movement.move_to)
        employee.save(update_fields=['basic_salary'])
        movement.status = 'APPROVED'
        movement.save(update_fields=['status'])
    elif movement.parameter.id == 8:
        payroll_key = f'P{movement.payroll_period.id}S{employee.pk}K{movement.earnings.id}'
        period_processor = PayrollProcessors.objects.get(payroll_key=payroll_key)
        working_days_processor = PayrollProcessors.objects. \
            get(payroll_key=f'P{movement.payroll_period.id}S{employee.pk}K78')

        if movement.earnings.id == 1:
            employee.basic_salary = Decimal(movement.move_to)
            employee.save(update_fields=['basic_salary'])
            period_processor.amount = Decimal(movement.move_to)
            period_processor.save(update_fields=['amount'])
        elif movement.earnings.id == 78:
            payroll_key = f'P{movement.payroll_period.id}S{employee.pk}K1'
            period_processor = PayrollProcessors.objects.get(payroll_key=payroll_key)
            new_amount = Decimal(movement.hours / 22.00) * employee.basic_salary
            working_days_processor.amount = Decimal(movement.hours)
            working_days_processor.save()
            period_processor.amount = round(new_amount)
            period_processor.save(update_fields=['amount'])
        elif movement.earnings.id == 1 and movement.move_to is None and Decimal(movement.hours) != working_days_processor.amount:
            working_days_processor = PayrollProcessors.objects. \
                get(payroll_key=f'P{movement.payroll_period.id}S{employee.pk}K78')
            working_days_processor.amount = Decimal(movement.hours)
            working_days_processor.save()
            new_amount = Decimal(movement.hours / 22.00) * employee.basic_salary
            period_processor.amount = new_amount
            period_processor.save(update_fields=['amount'])
        elif movement.earnings.id == 8:
            period_processor.amount += Decimal(str(round(float(movement.move_to))))
            period_processor.save(update_fields=['amount'])
        else:
            period_processor.amount = Decimal(movement.move_to)
            period_processor.save(update_fields=['amount'])

        movement.status = 'APPROVED'
        movement.save(update_fields=['status'])

    messages.success(request, f'{movement_name} successfully approved')
    return redirect('users:employee_movements_changelist')


def decline_employee_movement(request, movement_id):
    movement = EmployeeMovement.objects.filter(pk=movement_id).prefetch_related('employee', 'earnings').first()
    movement_name = f'{movement}'

    movement.status = 'DECLINED'
    movement.save(update_fields=['status'])

    # TODO: send email notification to requester and effected users

    messages.warning(request, f'Movement {movement_name} has been declined!')
    return render(request, 'users/employeemovement_list.html')


def load_overtime_factor(request):
    overtime_type = request.GET.get("overtime_type")
    period_id = int(request.GET.get("period_id"))
    user_id = int(request.GET.get("user_id"))
    hours = float(request.GET.get("hours"))
    employee = Employee.objects.get(pk=user_id)
    payroll_period = PayrollPeriod.objects.get(pk=period_id)
    period_processors = PayrollProcessors.objects.filter(payroll_period_id=payroll_period.id)\
        .filter(employee_id=employee.pk)

    factor = None
    if overtime_type == "NORMAL":
        factor = EarningDeductionType.objects.get(pk=8).factor
    elif overtime_type == "WEEKEND":
        factor = EarningDeductionType.objects.get(pk=19).factor

    basic_salary = period_processors.filter(earning_and_deductions_type_id=1).first().amount
    current_overtime = period_processors.filter(earning_and_deductions_type_id=8).first().amount

    overtime_amount = (basic_salary / Decimal(176)) * Decimal(factor) * Decimal(hours)

    overtime_amount += current_overtime

    response = {"overtime_amount": str(round(overtime_amount, 2))}

    return JsonResponse(response)
