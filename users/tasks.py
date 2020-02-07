import logging
import time

from celery import shared_task
from celery.task import task
from django.core.exceptions import ValidationError

from payroll.models import PayrollPeriod
from users.models import PayrollProcessors
from reports.models import NSSFReport
from reports.models import ExTraSummaryReportInfo

logger = logging.getLogger('payroll')


@shared_task
def process_nssf_nsif_reports(payroll_period_id):
    s = time.time()
    payroll_period = PayrollPeriod.objects.get(pk=payroll_period_id)
    payroll_key = payroll_period.payroll_key
    logger.info(f"Process NSS/NSIF reports for Period {payroll_period}")
    period_processes = PayrollProcessors.objects \
        .select_related('employee', 'employee__user', 'earning_and_deductions_type', 'earning_and_deductions_category',
                        'employee__nationality', 'employee__grade', 'employee__duty_station', 'employee__duty_country',
                        'employee__department', 'employee__job_title', 'employee__line_manager',
                        'employee__contract_type', 'employee__payroll_center', 'employee__bank_1',
                        'employee__bank_2', 'employee__category').filter(payroll_period=payroll_period)\
        .filter(payroll_period__payroll_center_id=payroll_period.payroll_center_id).all() \
        .prefetch_related('employee__report', 'employee__report__payroll_period')

    employees_in_period = set()
    for process in period_processes.iterator():
        employees_in_period.add(process.employee)

    for employee in employees_in_period:
        report_key = ''
        user_report = None
        try:
            report_key = f'{payroll_key}S{employee.pk}'
            user_report = ExTraSummaryReportInfo.objects.get(key=report_key)
        except ExTraSummaryReportInfo.DoesNotExist as e:
            logger.debug(e)
            logger.error(f"{employee} with extra report_is: {report_key} doesn\'t exist.")

        if NSSFReport.objects.filter(report_key=report_key).exists():
            report = NSSFReport.objects.get(report_key=report_key)
            report.payroll_period_id = payroll_period_id
            report.employee_id = employee.pk
            report.agresso_number = employee.agresso_number
            report.nsif_or_nssf_number = employee.nhif_number
            report.employee_full_name = employee.user.get_full_name()
            report.duty_station = employee.duty_station.duty_station
            report.cost_centre = employee.cost_centre
            report.job_title = employee.job_title.job_title
            report.user_extra_report = user_report
            report.save()
        else:
            employee_nsif = period_processes.filter(employee=employee).filter(earning_and_deductions_type_id=32).first()
            employer_nsif = period_processes.filter(employee=employee).filter(earning_and_deductions_type_id=31).first()
            nssf_report = NSSFReport(payroll_period_id=payroll_period_id,
                                     employee_id=employee.pk,
                                     agresso_number=employee.agresso_number,
                                     nsif_or_nssf_number=employee.nhif_number,
                                     employee_full_name=employee.user.get_full_name(),
                                     duty_station=employee.duty_station.duty_station,
                                     cost_centre=employee.cost_centre,
                                     job_title=employee.job_title.job_title,
                                     user_extra_report=user_report)
            nssf_report.save()
            nssf_report.earnings_and_deductions.add(employee_nsif, employer_nsif)

    e = time.time()
    print(f"Processed NSSF data in {e - s} seconds")
