import datetime
import logging
import time

import weasyprint
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.mail import get_connection, EmailMultiAlternatives
from django.db.models import Q
from django.forms import formset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from payroll.models import PayrollPeriod
from reports.helpers.mailer import Mailer
from support_data.forms import DeclinePayrollMessageForm
from users.forms import EarningsProcessUpdateForm, DeductionsProcessUpdateForm
from users.models import PayrollProcessors, Employee
from .forms import ReportGeneratorForm, ReconciliationReportGeneratorForm
from .models import ExTraSummaryReportInfo
from payroll.models import EarningDeductionType

logger = logging.getLogger('payroll')


@login_required
def display_summary_report(request, pk):
    payroll_period = get_object_or_404(PayrollPeriod, pk=pk)
    context = generate_summary_data(payroll_period, request.user)
    approval_message_form = DeclinePayrollMessageForm()

    context['approval_message_form'] = approval_message_form

    return render(request, 'reports/summary_report.html', context)


# generating summary data context
def generate_summary_data(payroll_period, system_user):
    if system_user.is_superuser:
        period_processes = PayrollProcessors.objects \
            .select_related('employee', 'earning_and_deductions_type', 'earning_and_deductions_category',
                            'employee__user', 'employee__job_title', 'employee__duty_station') \
            .filter(payroll_period_id=payroll_period.pk).all() \
            .prefetch_related('employee__report', 'employee__report__payroll_period')
    else:
        assigned_user_locations = list(system_user.employee.assigned_locations.all())
        period_processes = PayrollProcessors.objects \
            .select_related('employee', 'earning_and_deductions_type', 'earning_and_deductions_category',
                            'employee__user', 'employee__job_title', 'employee__duty_station') \
            .filter(payroll_period_id=payroll_period.pk).filter(employee__duty_station__in=assigned_user_locations).all() \
            .prefetch_related('employee__report', 'employee__report__payroll_period')
    employees_in_period = set()

    for process in period_processes.iterator():
        employees_in_period.add(process.employee)

    context = {
        'payroll_period': payroll_period,
        'period_processes': period_processes,
        'employees_to_process': employees_in_period,
    }
    return context


# noinspection PyPep8Naming
@login_required
def update_summary_report(request, pp, user):
    payroll_period = get_object_or_404(PayrollPeriod, pk=pp)
    employee = get_object_or_404(Employee, pk=user)
    processors = PayrollProcessors.objects \
        .select_related('employee', 'earning_and_deductions_type', 'earning_and_deductions_category', 'employee__user',
                        'employee__job_title', 'employee__duty_station', 'employee__category') \
        .filter(payroll_period=payroll_period).filter(employee=employee)

    # Categories: earning, deductions and statutory
    cat_e = processors.filter(earning_and_deductions_category=1).all()
    cat_d = processors.filter(earning_and_deductions_category=2).all()
    cat_s = processors.filter(earning_and_deductions_category=3).all()

    extra_data = ExTraSummaryReportInfo.objects.filter(key=f'{payroll_period.payroll_key}S{employee.pk}').first()

    # creating initial data for formsets
    e_data = [processor.to_dict() for processor in cat_e.iterator()]
    d_data = [processor.to_dict() for processor in cat_d.iterator()]
    s_data = [processor.to_dict() for processor in cat_s.iterator()]

    # creating initial display formsets
    e_FormSet = formset_factory(EarningsProcessUpdateForm, max_num=len(e_data), extra=0)
    d_FormSet = formset_factory(DeductionsProcessUpdateForm, max_num=len(d_data), extra=0)
    s_FormSet = formset_factory(DeductionsProcessUpdateForm, max_num=len(s_data), extra=0)

    if request.method == 'POST':
        e_formset = e_FormSet(request.POST, initial=e_data, prefix='earnings')
        d_formset = d_FormSet(request.POST, initial=d_data, prefix='deductions')
        s_formset = s_FormSet(request.POST, initial=s_data, prefix='statutory')

        if e_formset.is_valid() and d_formset.is_valid() and s_formset.is_valid():
            for form in e_formset:
                f = form.save(commit=False)
                f.employee = employee
                f.payroll_period = payroll_period
                f.earning_and_deductions_category_id = 1
                f.save()
            for form in d_formset:
                f = form.save(commit=False)
                f.employee = employee
                f.payroll_period = payroll_period
                f.earning_and_deductions_category_id = 2
                f.save()
            for form in s_formset:
                f = form.save(commit=False)
                f.employee = employee
                f.payroll_period = payroll_period
                f.earning_and_deductions_category_id = 3
                f.save()

            return HttpResponseRedirect(reverse('users:process_payroll-period',
                                                kwargs={'pk': payroll_period.id, 'user': user}))

    else:
        e_formset = e_FormSet(initial=e_data, prefix='earnings')
        d_formset = d_FormSet(initial=d_data, prefix='deductions')
        s_formset = s_FormSet(initial=s_data, prefix='statutory')

    context = {
        'payroll_period': payroll_period,
        'employee': employee,
        'e_formset': e_formset,
        'd_formset': d_formset,
        's_formset': s_formset,
        'extra_data': extra_data,
    }

    return render(request, 'reports/update_summary.html', context)


def generate(payroll_period, report, system_user):
    assigned_user_locations = []
    if not system_user.is_superuser:
        assigned_user_locations = list(system_user.employee.assigned_locations.all())
    results = dict()
    logger.info(f'generating {report} report data')
    if system_user.is_superuser:
        processors = PayrollProcessors.objects \
            .select_related('employee', 'payroll_period', 'payroll_period__payroll_center',
                            'earning_and_deductions_type',
                            'earning_and_deductions_category', 'employee__user', 'employee__job_title',
                            'employee__duty_country',
                            'employee__duty_station', 'employee__currency', 'employee__bank_1', 'employee__bank_2') \
            .filter(payroll_period_id=payroll_period.pk).all() \
            .prefetch_related('employee__report', 'employee__report__payroll_period').all()
    else:
        processors = PayrollProcessors.objects \
            .select_related('employee', 'payroll_period', 'payroll_period__payroll_center',
                            'earning_and_deductions_type',
                            'earning_and_deductions_category', 'employee__user', 'employee__job_title',
                            'employee__duty_country',
                            'employee__duty_station', 'employee__currency', 'employee__bank_1', 'employee__bank_2') \
            .filter(payroll_period_id=payroll_period.pk).filter(employee__duty_station__in=assigned_user_locations).all() \
            .prefetch_related('employee__report', 'employee__report__payroll_period').all()
    if payroll_period:
        if report == 'SUMMARY':
            if system_user.is_superuser:
                results[payroll_period] = PayrollProcessors.objects \
                    .select_related('employee', 'payroll_period', 'payroll_period__payroll_center',
                                    'earning_and_deductions_type',
                                    'earning_and_deductions_category', 'employee__user', 'employee__job_title',
                                    'employee__duty_country',
                                    'employee__duty_station', 'employee__currency', 'employee__bank_1',
                                    'employee__bank_2') \
                    .filter(payroll_period_id=payroll_period.pk).all() \
                    .prefetch_related('employee__report', 'employee__report__payroll_period').all()
            else:
                results[payroll_period] = PayrollProcessors.objects \
                    .select_related('employee', 'payroll_period', 'payroll_period__payroll_center',
                                    'earning_and_deductions_type',
                                    'earning_and_deductions_category', 'employee__user', 'employee__job_title',
                                    'employee__duty_country',
                                    'employee__duty_station', 'employee__currency', 'employee__bank_1',
                                    'employee__bank_2') \
                    .filter(payroll_period_id=payroll_period.pk).filter(employee__duty_station__in=assigned_user_locations).all() \
                    .prefetch_related('employee__report', 'employee__report__payroll_period').all()
        elif report == 'BANK' or report == 'CASH':
            if system_user.is_superuser:
                results[payroll_period] = PayrollProcessors.objects \
                    .select_related('employee', 'payroll_period', 'payroll_period__payroll_center',
                                    'earning_and_deductions_type',
                                    'earning_and_deductions_category', 'employee__user', 'employee__job_title',
                                    'employee__duty_country',
                                    'employee__duty_station', 'employee__currency', 'employee__bank_1',
                                    'employee__bank_2') \
                    .filter(payroll_period_id=payroll_period.pk).all() \
                    .prefetch_related('employee__report', 'employee__report__payroll_period') \
                    .filter(employee__payment_type=report).all()
            else:
                results[payroll_period] = PayrollProcessors.objects \
                    .select_related('employee', 'payroll_period', 'payroll_period__payroll_center',
                                    'earning_and_deductions_type',
                                    'earning_and_deductions_category', 'employee__user', 'employee__job_title',
                                    'employee__duty_country',
                                    'employee__duty_station', 'employee__currency', 'employee__bank_1',
                                    'employee__bank_2') \
                    .filter(payroll_period_id=payroll_period.pk).filter(employee__duty_station__in=assigned_user_locations).all() \
                    .prefetch_related('employee__report', 'employee__report__payroll_period') \
                    .filter(employee__payment_type=report).all()
        elif report == 'LEGER_EXPORT':
            results[payroll_period] = processors.exclude(amount=0)
        elif report == 'LST':
            p = processors.filter(earning_and_deductions_type_id=65).all()
            results[payroll_period] = p
        elif report == 'NSSF':
            p = processors.filter(Q(earning_and_deductions_type_id=32) | Q(earning_and_deductions_type_id=31)).all()
            results[payroll_period] = p
        elif report == 'PAYE':
            p = processors.filter(earning_and_deductions_type_id=61).all()
            earnings = processors.filter(earning_and_deductions_type__ed_category=1)
            results['earnings'] = earnings
            results[payroll_period] = p

    logger.debug(f'{report} report --> results: {results}')
    return results


def generate_leger_export(results, period):
    logger.debug('initializing leger export')

    results_data = results[period] \
        .prefetch_related('employee__employeeproject_set', 'employee__employeeproject_set__cost_center',
                          'employee__employeeproject_set__project_code')

    ed_types = EarningDeductionType.objects.filter(export='YES').all()

    data = {}
    for ed_type in ed_types.iterator():
        if ed_type.export == 'YES':
            processes = list(results_data.filter(earning_and_deductions_type_id=ed_type.pk).all())
            data[ed_type] = processes
            if ed_type.summarize == 'YES':
                total = 0
                c = 1
                for i in processes:
                    print(f'{ed_type} - earning for {i}: {c}')
                    total += i.amount
                    c = c + 1
                data[ed_type] = total

    return data


@login_required
@permission_required(('payroll.process_payrollperiod',), raise_exception=True)
def generate_reports(request):
    system_user = request.user
    if request.method == 'POST':
        form = ReportGeneratorForm(request.POST)
        if form.is_valid():
            payroll_center = form.cleaned_data.get('payroll_center')
            report = form.cleaned_data.get('report_type')
            year = form.cleaned_data.get('year')
            selected_month = form.cleaned_data.get('month')
            payroll_period = payroll_center.payrollperiod_set.select_related('payroll_center', 'created_by') \
                .filter(year=year).filter(month=selected_month).first()

            if payroll_period:
                extra_reports = ExTraSummaryReportInfo.objects.select_related('employee') \
                    .filter(payroll_period_id=payroll_period.pk).all()
                if extra_reports.exists():
                    logger.info(f'generating report data for {selected_month}-{year}')

                    results = generate(payroll_period, report, system_user)

                    earnings = None
                    if 'earnings' in results.keys():
                        earnings = results['earnings']
                        del results['earnings']

                    if report == 'LEGER_EXPORT':
                        results = generate_leger_export(results, payroll_period)

                    context = {
                        'title': report.capitalize() + ' Report',
                        'report': report,
                        'results': results,
                    }

                    if report == 'LEGER_EXPORT':
                        NUM_MONTHS = {
                            'JANUARY': 1,
                            'FEBRUARY': 2,
                            'MARCH': 3,
                            'APRIL': 4,
                            'MAY': 5,
                            'JUNE': 6,
                            'JULY': 7,
                            'AUGUST': 8,
                            'SEPTEMBER': 9,
                            'OCTOBER': 10,
                            'NOVEMBER': 11,
                            'DECEMBER': 12
                        }
                        context['trans_date'] = datetime.datetime(int(year), NUM_MONTHS[payroll_period.month], 28) \
                            .strftime("%d/%m/%Y")

                    if report == 'PAYE':
                        context['earnings'] = earnings
                        context['title'] = 'PIT'

                    if report == 'NSSF':
                        context['title'] = 'NSIF'

                    return render(request, 'reports/generated_report.html', context)
                else:
                    logger.error(f'PayrollPeriod ({payroll_period}) not processed yet!')
                    messages.warning(request, f'PayrollPeriod ({payroll_period}) has not been processed yet!')
                    return redirect('reports:generate-reports')
            else:
                logger.error(f'PayrollPeriod ({selected_month}) does not exist!')
                messages.warning(request, f'Reports for PayrollPeriod({selected_month}) don\'t exist.')
                return redirect('reports:generate-reports')
    else:
        form = ReportGeneratorForm()

    context = {
        'form': form,
        'title': 'Generate Reports'
    }
    return render(request, 'reports/generate_report.html', context)


@login_required
def generate_payslip_report(request, pp, user):
    period = get_object_or_404(PayrollPeriod, pk=pp)
    employee = get_object_or_404(Employee, pk=user)
    data = PayrollProcessors.objects.select_related('employee', 'earning_and_deductions_type',
                                                    'earning_and_deductions_category', 'employee__user',
                                                    'employee__job_title',
                                                    'employee__duty_station').filter(payroll_period=period).filter(
        employee=employee)
    report = 'Pay Slip'
    info_key = f'{period.payroll_key}S{employee.pk}'
    user_reports = ExTraSummaryReportInfo.objects.filter(key=info_key).all()

    context = {
        'report': report,
        'period': period,
        'data': data,
        'user_reports': user_reports,
    }

    return render(request, 'reports/generated_payslip_report.html', context)


@login_required
def send_mass_mail(request):
    response = {}
    if request.method == 'POST':
        users = request.POST.getlist('users[]')
        period_id = request.POST.get('payroll_period')
        employees = [Employee.objects.filter(agresso_number=sap_no).first() for sap_no in users]
        payroll_period = get_object_or_404(PayrollPeriod, pk=int(period_id))
        emails = []
        user_payslip_data = dict()
        for employee in employees:
            data = PayrollProcessors.objects.filter(payroll_period=payroll_period).filter(employee=employee)
            info_key = f'{payroll_period.payroll_key}S{employee.pk}'
            user_reports = ExTraSummaryReportInfo.objects.filter(key=info_key).all()
            context = {
                'report': 'PaySlip',
                'period': payroll_period,
                'data': data,
                'user_reports': user_reports,
            }
            user_payslip_data[employee.user.email] = context

        mailer = Mailer(settings.DEFAULT_FROM_EMAIL)
        subject = f'PAYSLIP FOR MONTH OF {payroll_period.month}'
        body = f'Please find attached your payslip for {payroll_period.month}.\nKindly report to the finance department for any inquires\n\nWarm regards\nFinance Department'
        template = 'partials/payslip.html'
        mailer.send_messages(subject, body, user_payslip_data, request, template=template)

        response = {'status': 'success'}

    return JsonResponse(response)


def get_user_processors(processors, employee):
    return processors.filter(employee=employee)


def get_category_processors(processors, category_id):
    return processors.filter(earning_and_deductions_category=category_id)


class ReconciliationUserData:

    def __init__(self, user):
        self.user = user
        self._earnings_data = {}
        self._deductions_data = {}
        self._statutory_data = {}
        self._extra_data = {}

    def add_earnings_data(self, ed_type, amount):
        self._earnings_data[ed_type] = amount

    def get_earnings_data(self):
        return self._earnings_data

    def add_deductions_data(self, ed_type, amount):
        self._deductions_data[ed_type] = amount

    def get_deductions_data(self):
        return self._deductions_data

    def add_statutory_data(self, ed_type, amount):
        self._statutory_data[ed_type] = amount

    def get_statutory_data(self):
        return self._statutory_data

    def add_extra_data(self, ed_type, amount):
        self._extra_data[ed_type] = amount

    def get_extra_data(self):
        return self._extra_data


def get_reconciled_amount(processor_1, processor_2):
    return processor_1[0] - processor_2[0]


@login_required
def generate_reconciliation_report(request):
    if request.method == 'POST':
        form = ReconciliationReportGeneratorForm(request.POST)
        if form.is_valid():
            period_one = form.cleaned_data.get('first_payroll_period')
            period_two = form.cleaned_data.get('second_payroll_period')
            logger.info(f'reconciling {period_one} and {period_two}')
            context_1 = generate_summary_data(period_one, request.user)
            context_2 = generate_summary_data(period_two, request.user)

            employees_in_both_periods = set(context_1['employees_to_process']) \
                .intersection(set(context_2['employees_to_process']))
            logger.info(f'Employees in both periods {employees_in_both_periods}')

            # only in period 1
            employees_only_in_period_1 = set(context_1['employees_to_process']) \
                .difference(employees_in_both_periods)
            logger.info(f'Employees in both periods {employees_only_in_period_1}')

            # only in period 2
            employees_only_in_period_2 = set(context_2['employees_to_process']) \
                .difference(employees_in_both_periods)
            logger.info(f'Employees in both periods {employees_only_in_period_2}')

            reconciliation_data = []
            if employees_in_both_periods:
                for employee in employees_in_both_periods:
                    logger.info(f'Getting user processors for {employee}')
                    user_processors_data_1 = get_user_processors(context_1['period_processes'], employee)
                    user_processors_data_2 = get_user_processors(context_2['period_processes'], employee)

                    logger.info(f'Getting user Extra reports for {employee}')
                    period_one_extra_data = ExTraSummaryReportInfo.objects.filter(
                        payroll_period=period_one).filter(employee=employee) \
                        .values('gross_earning', 'total_deductions', 'net_pay').first()
                    period_two_extra_data = ExTraSummaryReportInfo.objects.filter(
                        payroll_period=period_two).filter(employee=employee) \
                        .values('gross_earning', 'total_deductions', 'net_pay').first()

                    # earnings reconciliation
                    logger.info(f'Getting user earnings processors for {employee}')
                    user_earnings_1 = get_category_processors(user_processors_data_1, 1) \
                        .select_related('employee', 'earning_and_deductions_type')
                    user_earnings_2 = get_category_processors(user_processors_data_2, 1) \
                        .select_related('employee', 'earning_and_deductions_type')

                    earning_set_1 = set([earning.earning_and_deductions_type for earning in user_earnings_1])
                    earning_set_2 = set([earning.earning_and_deductions_type for earning in user_earnings_2])

                    # deductions reconciliation
                    logger.info(f'Getting user deductions processors for {employee}')
                    user_deductions_1 = get_category_processors(user_processors_data_1, 2) \
                        .select_related('employee', 'earning_and_deductions_type')
                    user_deductions_2 = get_category_processors(user_processors_data_2, 2) \
                        .select_related('employee', 'earning_and_deductions_type')

                    deductions_set_1 = set([earning.earning_and_deductions_type for earning in user_deductions_1])
                    deductions_set_2 = set([earning.earning_and_deductions_type for earning in user_deductions_2])

                    # statutory reconciliation
                    logger.info(f'Getting user statutory processors for {employee}')
                    user_statutory_1 = get_category_processors(user_processors_data_1, 3) \
                        .select_related('employee', 'earning_and_deductions_type')
                    user_statutory_2 = get_category_processors(user_processors_data_2, 3) \
                        .select_related('employee', 'earning_and_deductions_type')

                    statutory_set_1 = set([earning.earning_and_deductions_type for earning in user_statutory_1])
                    statutory_set_2 = set([earning.earning_and_deductions_type for earning in user_statutory_2])

                    logger.info(f'Getting user processors that a similar in both periods for {employee}')
                    earnings_in_both = earning_set_1.intersection(earning_set_2)
                    deductions_in_both = deductions_set_1.intersection(deductions_set_2)
                    statutory_in_both = statutory_set_1.intersection(statutory_set_2)

                    user_rec_data = ReconciliationUserData(employee)
                    logger.info(f'Reconciling earnings for {employee}')
                    if earnings_in_both:
                        for earning in earnings_in_both:
                            e_processor_1 = user_earnings_1.filter(earning_and_deductions_type_id=earning.pk) \
                                .values_list('amount').first()
                            e_processor_2 = user_earnings_2.filter(earning_and_deductions_type_id=earning.pk) \
                                .values_list('amount').first()

                            amount = get_reconciled_amount(e_processor_1, e_processor_2)

                            user_rec_data.add_earnings_data(earning.ed_type, amount)

                    logger.info(f'Reconciling deductions for {employee}')
                    if deductions_in_both:
                        for earning in deductions_in_both:
                            d_processor_1 = user_deductions_1.filter(earning_and_deductions_type_id=earning.pk) \
                                .values_list('amount').first()
                            d_processor_2 = user_deductions_2.filter(earning_and_deductions_type_id=earning.pk) \
                                .values_list('amount').first()

                            amount = get_reconciled_amount(d_processor_1, d_processor_2)

                            user_rec_data.add_deductions_data(earning.ed_type, amount)

                    logger.info(f'Reconciling statutory for {employee}')
                    if statutory_in_both:
                        for earning in statutory_in_both:
                            s_processor_1 = user_statutory_1.filter(earning_and_deductions_type_id=earning.pk) \
                                .values_list('amount').first()
                            s_processor_2 = user_statutory_2.filter(earning_and_deductions_type_id=earning.pk) \
                                .values_list('amount').first()

                            amount = get_reconciled_amount(s_processor_1, s_processor_2)

                            user_rec_data.add_statutory_data(earning.ed_type, amount)

                    logger.info(f'Reconciling extra report for {employee}')
                    amount = period_one_extra_data['total_deductions'] - period_two_extra_data['total_deductions']
                    user_rec_data.add_extra_data('Total Deductions', amount)

                    amount = period_one_extra_data['gross_earning'] - period_two_extra_data['gross_earning']
                    user_rec_data.add_extra_data('Gross Salary', amount)

                    amount = period_one_extra_data['net_pay'] - period_two_extra_data['net_pay']
                    user_rec_data.add_extra_data('Net Pay', amount)

                    reconciliation_data.append(user_rec_data)

            if employees_only_in_period_1:
                for employee in employees_only_in_period_1:
                    logger.info(f'Getting user processors for {employee}')
                    user_processors_data_1 = get_user_processors(context_1['period_processes'], employee)

                    logger.info(f'Getting user Extra reports for {employee}')
                    period_one_extra_data = ExTraSummaryReportInfo.objects.filter(
                        payroll_period=period_one).filter(employee=employee) \
                        .values_list('gross_earning', 'total_deductions', 'net_pay').firs()

                    # earnings reconciliation
                    logger.info(f'Getting user earnings processors for {employee}')
                    user_earnings_1 = get_category_processors(user_processors_data_1, 1) \
                        .select_related('employee', 'earning_and_deductions_type')

                    earning_set_1 = set([earning.earning_and_deductions_type for earning in user_earnings_1])

                    # deductions reconciliation
                    logger.info(f'Getting user deductions processors for {employee}')
                    user_deductions_1 = get_category_processors(user_processors_data_1, 2) \
                        .select_related('employee', 'earning_and_deductions_type')

                    deductions_set_1 = set([earning.earning_and_deductions_type for earning in user_deductions_1])

                    # statutory reconciliation
                    logger.info(f'Getting user statutory processors for {employee}')
                    user_statutory_1 = get_category_processors(user_processors_data_1, 3) \
                        .select_related('employee', 'earning_and_deductions_type')

                    statutory_set_1 = set([earning.earning_and_deductions_type for earning in user_statutory_1])

                    user_rec_data = ReconciliationUserData(employee)
                    logger.info(f'Reconciling earnings for {employee}')
                    for earning in earning_set_1:
                        e_processor_1 = user_earnings_1.filter(earning_and_deductions_type_id=earning.pk) \
                            .values_list('amount').first()

                        user_rec_data.add_earnings_data(earning.ed_type, e_processor_1[0])

                    logger.info(f'Reconciling deductions for {employee}')
                    for earning in deductions_set_1:
                        d_processor_1 = user_deductions_1.filter(earning_and_deductions_type_id=earning.pk) \
                            .values_list('amount').first()

                        user_rec_data.add_deductions_data(earning, d_processor_1[0])

                    logger.info(f'Reconciling statutory for {employee}')
                    for earning in statutory_set_1:
                        s_processor_1 = user_statutory_1.filter(earning_and_deductions_type_id=earning.pk) \
                            .values_list('amount').first()

                        user_rec_data.add_statutory_data(earning, s_processor_1[0])

                    logger.info(f'Reconciling extra report for {employee}')
                    user_rec_data.add_extra_data('Total Deductions', period_one_extra_data['total_deductions'])

                    user_rec_data.add_extra_data('Gross Salary', period_one_extra_data['gross_earning'])

                    user_rec_data.add_extra_data('Net Pay', period_one_extra_data['net_pay'])

                    reconciliation_data.append(user_rec_data)

            if employees_only_in_period_2:
                for employee in employees_only_in_period_2:
                    logger.info(f'Getting user processors for {employee}')
                    user_processors_data_2 = get_user_processors(context_2['period_processes'], employee)

                    logger.info(f'Getting user Extra reports for {employee}')
                    period_two_extra_data = ExTraSummaryReportInfo.objects.filter(
                        payroll_period=period_two).filter(employee=employee) \
                        .values_list('gross_earning', 'total_deductions', 'net_pay').first()

                    # earnings reconciliation
                    logger.info(f'Getting user earnings processors for {employee}')
                    user_earnings_2 = get_category_processors(user_processors_data_2, 1) \
                        .select_related('employee', 'earning_and_deductions_type')

                    earning_set_2 = set([earning.earning_and_deductions_type for earning in user_earnings_2])

                    # deductions reconciliation
                    logger.info(f'Getting user deductions processors for {employee}')
                    user_deductions_2 = get_category_processors(user_processors_data_2, 2) \
                        .select_related('employee', 'earning_and_deductions_type')

                    deductions_set_2 = set([earning.earning_and_deductions_type for earning in user_deductions_2])

                    # statutory reconciliation
                    logger.info(f'Getting user statutory processors for {employee}')
                    user_statutory_2 = get_category_processors(user_processors_data_2, 3) \
                        .select_related('employee', 'earning_and_deductions_type')

                    statutory_set_2 = set([earning.earning_and_deductions_type for earning in user_statutory_2])

                    user_rec_data = ReconciliationUserData(employee)
                    logger.info(f'Reconciling earnings for {employee}')
                    for earning in earning_set_2:
                        e_processor_2 = user_earnings_2.filter(earning_and_deductions_type_id=earning.pk) \
                            .values_list('amount').first()

                        user_rec_data.add_earnings_data(earning.ed_type, e_processor_2[0])

                    logger.info(f'Reconciling deductions for {employee}')
                    for earning in deductions_set_2:
                        d_processor_2 = user_deductions_2.filter(earning_and_deductions_type_id=earning.pk) \
                            .values_list('amount').first()

                        user_rec_data.add_deductions_data(earning, d_processor_2[0])

                    logger.info(f'Reconciling statutory for {employee}')
                    for earning in statutory_set_2:
                        s_processor_2 = user_statutory_2.filter(earning_and_deductions_type_id=earning.pk) \
                            .values_list('amount').first()

                        user_rec_data.add_statutory_data(earning, s_processor_2[0])

                    logger.info(f'Reconciling extra report for {employee}')
                    user_rec_data.add_extra_data('Total Deductions', period_two_extra_data['total_deductions'])

                    user_rec_data.add_extra_data('Gross Salary', period_two_extra_data['gross_earning'])

                    user_rec_data.add_extra_data('Net Pay', period_two_extra_data['net_pay'])

                    reconciliation_data.append(user_rec_data)

            context = {
                'period_1': period_one,
                'period_2': period_two,
                'data': reconciliation_data
            }
            return render(request, 'reports/generated_reconciliation_report.html', context)
    else:
        form = ReconciliationReportGeneratorForm()

    context = {
        'tile': 'Reconcile Payroll Periods',
        'form': form
    }

    return render(request, 'reports/generate_reconciliation_report.html', context)
