from datetime import datetime


PAYROLL_YEARS = [(year, year) for year in range(datetime.now().year-1, datetime.now().year + 10)]

month_str = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY',
             'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER',
             'NOVEMBER', 'DECEMBER']

MONTHS = [(month_str[month-1], month_str[month-1]) for month in range(1, 13)]

KV_MONTH = {
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
        'DECEMBER': 12,
    }

DISPLAY_NUMS = {
        1: 1,
        11: 2,
        8: 3,
        2: 4,
        4: 5,
        16: 6,
        32: 7,
        61: 8,
        75: 9,
        64: 10,
        67: 11,
        66: 12,
        65: 13,
        26: 14,
        77: 15,
        78: 16,
        79: 17,
        20: 18,
        63: 19
    }