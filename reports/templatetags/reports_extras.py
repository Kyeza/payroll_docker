from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def obj_type(obj):
    return type(obj)


@register.filter
def get_distinct_employee_set(processors):
    employees_in_period = set()
    for process in processors.iterator():
        employees_in_period.add(process.employee)

    return employees_in_period


@register.filter
def credit(amount):
    return amount * -1


@register.filter
def total_amount(processors):
    total = 0
    for inst in processors:
        for k, amount in inst.items():
            total += amount
    return total


@register.filter
def bank_percentage(net_pay, percentage):
    if percentage:
        return round(net_pay * Decimal((percentage/100)), 2)
    else:
        return net_pay


@register.filter
def contains_time(value):
    if value.__contains__('time'):
        return True
    return False
