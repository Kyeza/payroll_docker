from __future__ import absolute_import, unicode_literals

import datetime
import logging

from celery import shared_task, task
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import get_connection

from payroll.models import PayrollPeriod, PayrollCenterEds
from reports.helpers.mailer import Mailer
from users.models import Employee, PayrollProcessors, User


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
