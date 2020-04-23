from __future__ import absolute_import, unicode_literals

import datetime
import logging
from decimal import Decimal

from celery import shared_task, task
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.mail import get_connection
from django.db.models import Q

from payroll.models import PayrollPeriod, PayrollCenterEds, EarningDeductionType
from reports.helpers.mailer import Mailer
from reports.models import ExTraSummaryReportInfo, SocialSecurityReport, TaxationReport, CashReport, BankReport
from support_data.models import SudaneseTaxRates
from users.models import Employee, PayrollProcessors, User, Notification


@shared_task
def send_bulk_emails(emails):
    """task for  sending emails in bulk

    args: emails

    return: string
    """
    connection = get_connection()
    connection.send_messages(emails)

    return f'{len(emails)} email(s) have been successfully sent'


@task()
def notify_user_on_contract_expiry():
    group = Group.objects.get(pk=8)
    hr_staff = group.user_set.all()

    staff_emails = []
    for staff in hr_staff:
        staff_emails.append(staff.email)

    all_users = Employee.objects.filter(employement_status='APPROVED').all()
    mailer = Mailer(settings.DEFAULT_FROM_EMAIL)
    if all_users:
        date_now = datetime.date.today()
        for user in all_users.iterator():
            timedelta = user.contract_expiry - date_now
            timedelta_rv = date_now - user.contract_expiry
            if timedelta.days < 0:
                subject = 'EMPLOYEE CONTRACT EXPIRED'
                body = f'Hello,\n This email is a reminder that the contract for {user.user.get_full_name()} expired {timedelta_rv} ago'
                staff_emails.append(user.user.email)
                mailer.send_messages(subject, body, staff_emails)
                staff_emails.remove(user.user.email)
            elif timedelta.days in range(32):
                subject = 'EMPLOYEE CONTRACT ABOUT TO EXPIRE'
                body = f'Hello,\n This email is a reminder that the contract for {user.user.get_full_name()} will expire in {timedelta}'
                staff_emails.append(user.user.email)
                mailer.send_messages(subject, body, staff_emails)
                staff_emails.remove(user.user.email)


logger = logging.getLogger('payroll')


@shared_task
def add_users_for_period(payroll_period_id, instance_id):
    payroll_period = PayrollPeriod.objects.get(pk=payroll_period_id)
    instance = User.objects.get(pk=instance_id)
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


@shared_task
def add_user_to_payroll_processor(instance_id, payroll_period_id=None):
    payroll_period = None
    if payroll_period_id is not None:
        payroll_period = PayrollPeriod.objects.get(pk=payroll_period_id)
    instance = User.objects.get(pk=instance_id)
    logger.debug(f'adding user: {instance} to payroll processor')
    user_status = instance.employee.employment_status
    if payroll_period is not None:
        add_users_for_period.delay(payroll_period_id, instance_id)
    else:
        payroll_periods = instance.employee.payroll_center.payrollperiod_set.all()
        if user_status == 'APPROVED' or user_status == 'REACTIVATED':
            if payroll_periods.exists():
                open_payroll_period = payroll_periods.filter(status='OPEN').all()
                if open_payroll_period.exists():
                    for payroll_period in open_payroll_period:
                        add_users_for_period.delay(payroll_period.id, instance_id)
                else:
                    logger.error(f'No OPEN payroll periods in the Processor')
            else:
                logger.error(f'No PayrollPeriods in the Processor')
        else:
            logger.error(f'{instance} either not APPROVED or REACTIVATED')


@shared_task
def processor(request_user_id, payroll_period_id, process_with_rate=None, method='GET', user_id=None):
    request_user = User.objects.get(pk=request_user_id)
    payroll_period = PayrollPeriod.objects.get(pk=payroll_period_id)
    Notification.objects.create(to_user=request_user)
    user = None
    if user_id is not None:
        user = Employee.objects.get(pk=user_id)

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

    users = payroll_center.employee_set.select_related('user').all()
    employees_in_period = set()
    if users.exists() and user is None:
        logger.critical(f'Adding Payroll center users for Period {payroll_period} to processor')
        for employee in users:
            if employee.employment_status == 'APPROVED':
                inst = employee.user
                try:
                    add_user_to_payroll_processor.delay(inst.id, payroll_period.id)
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
            .select_related('employee', 'employee__user', 'earning_and_deductions_type',
                            'earning_and_deductions_category',
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
            .select_related('employee', 'employee__user', 'earning_and_deductions_type',
                            'earning_and_deductions_category',
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
    current_tax_rates = list(SudaneseTaxRates.objects.all())
    if current_tax_rates:
        for i, tax_bracket in enumerate(current_tax_rates):
            if i < len(current_tax_rates) - 1:
                tax_bracket.actual_usd = round(
                    (tax_bracket.upper_ssp_bound - tax_bracket.lower_ssp_bound) / Decimal(process_with_rate))
            if 0 < i < len(current_tax_rates) - 1:
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

        basic_salary = period_processes.filter(employee=employee).filter(
            earning_and_deductions_type_id=1).first().amount

        arrears = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=11).first()

        # calculating NHIF
        logger.info(f'Processing for user {employee}: calculating NHIF')
        employee_nhif = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=32).first()
        if employee_nhif:
            employee_nhif.amount = round((basic_salary + arrears.amount) * Decimal(nhif_ed_type.factor))
            nhif_8 = employee_nhif.amount
            employee_nhif.save(update_fields=['amount'])

        # calculating Taxable gross earnings
        taxable_gross_earnings = gross_earnings - employee_nhif.amount

        # calculating PIT
        logger.info(f'Processing for user {employee}: calculating PIT')

        rates = []
        for rate in current_tax_rates:
            rates.append(rate)

        accumulated_actual_usd_amounts = []
        for i, rate in enumerate(rates):
            if i == len(rates) - 1:
                taxable_gross_earnings = taxable_gross_earnings * Decimal(rate.tax_rate)
                pit = taxable_gross_earnings + \
                      sum(accumulated_actual_usd_amounts) if accumulated_actual_usd_amounts else 0
                break
            elif int(taxable_gross_earnings) <= int(rate.actual_usd):
                rate_before = rates[i - 1]
                taxable_gross_earnings = taxable_gross_earnings * Decimal(rate.tax_rate)
                pit = taxable_gross_earnings + \
                      sum(accumulated_actual_usd_amounts) if accumulated_actual_usd_amounts else 0
                break
            else:
                taxable_gross_earnings = taxable_gross_earnings - rate.actual_usd
                if rate.actual_usd_taxable_amount is not None:
                    accumulated_actual_usd_amounts.append(rate.actual_usd_taxable_amount)

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
        if employer_pension:
            employer_pension.amount = (basic_salary + arrears.amount) / Decimal(12)
            employer_pension.save(update_fields=['amount'])

        # update NSSF 17% if exists in payroll center
        logger.info(f'Processing for user {employee}: updating NHIF 17%')
        employee_nhif_17_processor = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_type_id=31).first()
        if employee_nhif_17_processor:
            employee_nhif_17_processor.amount = round((basic_salary + arrears.amount) * Decimal(nhif_ed_type_17.factor))
            nhif_17 = employee_nhif_17_processor.amount
            employee_nhif_17_processor.save(update_fields=['amount'])

        tx_data_ded = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_category_id=2).all()
        tx_data_stat = period_processes.filter(employee=employee) \
            .filter(earning_and_deductions_category_id=3).all()

        # calculating total deductions from deductions
        logger.info(f'Processing for user {employee}: calculating total deductions from deductions')
        try:
            if tx_data_ded.exists():
                for inst in tx_data_ded.iterator():
                    if inst.amount:
                        total_deductions += inst.amount
                    else:
                        inst.amount = 0
                        inst.save()
                        total_deductions += inst.amount

        except Exception as e:
            logger.info(f'error: {e}')

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

        report_id = f'{payroll_period.payroll_key}S{employee.pk}'
        update_or_create_user_summary_report.delay(report_id, employee.pk, net_pay, total_deductions, gross_earnings,
                                                   payroll_period_id)
        update_or_create_user_social_security_report.delay(report_id, employee.pk, payroll_period_id)
        update_or_create_user_taxation_report.delay(report_id, employee.pk, payroll_period_id)
        update_or_create_user_bank_report.delay(report_id, employee.pk, payroll_period_id)
        update_or_create_user_cash_report.delay(report_id, employee.pk, payroll_period_id)

        logger.info(f'Successfully processed {employee} Payroll Period')

    response['message'] = f'Successfully process Payroll Period with dollar rate of {process_with_rate}'
    response['status'] = 'Success'
    logger.info(f'Finished processing {response}')

    if method == 'POST':
        logger.debug(f'Displaying report {response}')
        return response


@shared_task
def update_or_create_user_summary_report(report_id, user_id, net_pay, total_deductions, gross_earnings, period_id):
    report, created = ExTraSummaryReportInfo.objects.get_or_create(key=report_id)
    employee = User.objects.get(pk=user_id).employee
    processors = PayrollProcessors.objects.filter(payroll_period_id=period_id).filter(employee_id=user_id)

    try:
        report.employee_name = employee.user.get_full_name()
        report.analysis = employee.agresso_number
        report.job_title = employee.job_title.job_title
        report.employee_id = employee.pk

        earnings = processors.filter(earning_and_deductions_type__display_number__lt=7).all()
        deductions = processors.filter(earning_and_deductions_type__display_number__gt=6) \
            .filter(earning_and_deductions_type__display_number__lt=21).all()

        if not created:
            report.earnings_to_display.clear()
            report.deductions_to_display.clear()

        for earning in earnings.iterator():
            report.earnings_to_display.add(earning)

        for deduction in deductions.iterator():
            report.deductions_to_display.add(deduction)

        report.net_pay = net_pay
        report.gross_earning = gross_earnings
        report.total_deductions = total_deductions
        report.save()
    except (Exception, AttributeError) as e:
        logger.error(f'an error occurred while processing summary report for {employee.user.get_full_name()}')
        logger.error(e.args)
        report.delete()

    if created:
        logger.info(f'created summary report for {employee.user.get_full_name()}')
    else:
        logger.info(f'updated summary report for {employee.user.get_full_name()}')


# noinspection DuplicatedCode
@shared_task
def update_or_create_user_social_security_report(report_id, user_id, period_id):
    report, created = SocialSecurityReport.objects.get_or_create(report_id=report_id)
    employee = User.objects.get(pk=user_id).employee
    try:
        report.period = PayrollPeriod.objects.filter(pk=period_id).values_list('month').first()[0]
        report.agresso_number = employee.agresso_number
        report.social_security_number = employee.social_security_number
        report.staff_full_name = employee.user.get_full_name()
        report.duty_station = employee.duty_station.duty_station
        report.cost_centre = employee.cost_centre.cost_centre
        report.job_title = employee.job_title.job_title
        report.summary_report = ExTraSummaryReportInfo.objects.get(key=report_id)
        processors = PayrollProcessors.objects.filter(payroll_period_id=period_id).filter(employee_id=user_id) \
            .filter(Q(earning_and_deductions_type_id=32) | Q(earning_and_deductions_type_id=31)).all()

        if not created:
            report.earnings.clear()

        for item in processors.iterator():
            report.earnings.add(item)
        report.save()
    except (Exception, AttributeError) as e:
        logger.error(f'an error occurred while processing social security report for {employee.user.get_full_name()}')
        logger.error(e.args)
        report.delete()

    if created:
        logger.info(f'created social security report for {employee.user.get_full_name()}')
    else:
        logger.info(f'updated social security report for {employee.user.get_full_name()}')


# noinspection DuplicatedCode
@shared_task
def update_or_create_user_taxation_report(report_id, user_id, period_id):
    report, created = TaxationReport.objects.get_or_create(report_id=report_id)
    employee = User.objects.get(pk=user_id).employee
    try:
        report.period = PayrollPeriod.objects.filter(pk=period_id).values_list('month').first()[0]
        report.agresso_number = employee.agresso_number
        report.staff_full_name = employee.user.get_full_name()
        report.cost_centre = employee.cost_centre.cost_centre
        report.tin_number = employee.tin_number
        report.summary_report = ExTraSummaryReportInfo.objects.get(key=report_id)
        earnings = PayrollProcessors.objects.filter(payroll_period_id=period_id).filter(employee_id=user_id) \
            .filter(earning_and_deductions_type__display_number__lt=7).all()
        deductions = PayrollProcessors.objects.filter(payroll_period_id=period_id).filter(employee_id=user_id) \
            .filter(earning_and_deductions_type_id=61).all()

        if not created:
            report.earnings.clear()
            report.deductions.clear()

        for item in earnings.iterator():
            report.earnings.add(item)
        for item in deductions.iterator():
            report.deductions.add(item)
        report.save()
    except (Exception, AttributeError) as e:
        logger.error(f'an error occurred while processing taxation report for {employee.user.get_full_name()}')
        logger.error(e.args)
        report.delete()

    if created:
        logger.info(f'created taxation report for {employee.user.get_full_name()}')
    else:
        logger.info(f'updated taxation report for {employee.user.get_full_name()}')


# noinspection DuplicatedCode
@shared_task
def update_or_create_user_bank_report(report_id, user_id, period_id):
    employee = User.objects.get(pk=user_id).employee
    if employee.payment_type == 'BANK':
        if employee.bank_1 is not None:
            report, created = BankReport.objects.get_or_create(report_id=report_id)
            try:
                report.period = PayrollPeriod.objects.filter(pk=period_id).values_list('month').first()[0]
                report.agresso_number = employee.agresso_number
                report.staff_full_name = employee.user.get_full_name()
                report.payment_location = employee.payment_location.duty_station
                report.bank = employee.bank_1.bank
                report.branch = employee.bank_1.branch
                report.sort_code = employee.bank_1.sort_code
                report.account_number = employee.first_account_number
                report.summary_report = ExTraSummaryReportInfo.objects.get(key=report_id)
            except (Exception, AttributeError) as e:
                logger.error(f'an error occurred while processing bank report for {employee.user.get_full_name()}')
                logger.error(e.args)
                report.delete()

            if created:
                logger.info(f'created bank report 1 for {employee.user.get_full_name()}')
            else:
                logger.info(f'updated bank report 1 for {employee.user.get_full_name()}')

        if employee.bank_2 is not None:
            report, created = BankReport.objects.get_or_create(report_id=report_id)
            try:
                report.period = PayrollPeriod.objects.filter(pk=period_id).values_list('month').first()[0]
                report.agresso_number = employee.agresso_number
                report.staff_full_name = employee.user.get_full_name()
                report.payment_location = employee.payment_location.duty_station
                report.bank = employee.bank_2.bank
                report.branch = employee.bank_2.branch
                report.sort_code = employee.bank_2.sort_code
                report.account_number = employee.second_account_number
                report.summary_report = ExTraSummaryReportInfo.objects.get(key=report_id)
            except (Exception, AttributeError) as e:
                logger.error(f'an error occurred while processing bank report for {employee.user.get_full_name()}')
                logger.error(e.args)
                report.delete()

            if created:
                logger.info(f'created bank report 2 for {employee.user.get_full_name()}')
            else:
                logger.info(f'updated bank report 2 for {employee.user.get_full_name()}')


@shared_task
def update_or_create_user_cash_report(report_id, user_id, period_id):
    employee = User.objects.get(pk=user_id).employee
    if employee.payment_type == 'CASH':
        report, created = CashReport.objects.get_or_create(report_id=report_id)
        try:
            report.period = PayrollPeriod.objects.filter(pk=period_id).values_list('month').first()[0]
            report.agresso_number = employee.agresso_number
            report.staff_full_name = employee.user.get_full_name()
            report.job_title = employee.job_title.job_title
            report.payment_location = employee.payment_location.duty_station
            report.payment_type = employee.payment_type
            report.summary_report = ExTraSummaryReportInfo.objects.get(key=report_id)
        except (Exception, AttributeError) as e:
            logger.error(f'an error occurred while processing cash report for {employee.user.get_full_name()}')
            logger.error(e.args)
            report.delete()

        if created:
            logger.info(f'created cash report for {employee.user.get_full_name()}')
        else:
            logger.info(f'updated cash report for {employee.user.get_full_name()}')
