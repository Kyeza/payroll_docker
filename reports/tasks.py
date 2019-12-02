from __future__ import absolute_import, unicode_literals

import datetime

from celery import shared_task, task
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import get_connection

from reports.helpers.mailer import Mailer
from users.models import Employee


@shared_task
def send_bulk_emails(emails):
    """task for  sending emails in bulk

    args: emails

    return: string
    """
    connection = get_connection()
    connection.send_messages(emails)

    return f'{len(emails)} email(s) have been successfully sent'


@shared_task
def sample_task(a, b):
    return f'result of addition is {a + b}'


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


@task()
def task_number_one():
    print("I love Kyeza Arnold")
