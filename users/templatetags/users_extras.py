from django import template
from django.http import HttpRequest

register = template.Library()


@register.filter
def category(processors, category_id):
    data = processors.filter(earning_and_deductions_category_id=category_id).all()
    return data


@register.filter
def category_display(processors, category_id):
    if category_id == 1:
        data = processors.filter(earning_and_deductions_type__display_number__lt=7).all()
    else:
        data = processors.filter(earning_and_deductions_type__display_number__gt=6)\
            .filter(earning_and_deductions_type__display_number__lt=21).all()

    return data


@register.filter
def user_data(processors, staff):
    data = processors.filter(employee_id=staff.pk).values('amount')\
        .order_by('earning_and_deductions_type__display_number').all()
    return list(data)


@register.filter
def user_data_headings(processors, staff):
    return processors.filter(employee_id=staff.pk).values('earning_and_deductions_type__ed_type')\
        .order_by('earning_and_deductions_type__display_number').all()


@register.filter
def payslip_data(processors, staff):
    return processors.filter(employee_id=staff.pk).values('earning_and_deductions_type__ed_type', 'amount')


@register.filter
def report_key(payroll_period, staff):
    return f'{payroll_period.payroll_key}S{staff.id_number}'


@register.filter
def report(staff, period):
    return staff.report.filter(payroll_period=period).first()


@register.filter
def user_profile(user):
    try:
        if user:
            return user.employee
        else:
            return None
    except Exception:
        return None
