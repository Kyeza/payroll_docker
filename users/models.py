from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from hr_system.constants import YES_OR_NO_TYPES
from .constants import MARITAL_STATUS, GENDER, EMP_STATUS
from .utils import get_image_filename, get_doc_filename


class User(AbstractUser):
    middle_name = models.CharField(max_length=100, blank=True, null=True)

    def get_full_name(self):
        full_name = ''
        if self.first_name:
            full_name += self.first_name + " "
        if self.middle_name:
            full_name += self.middle_name + " "
        if self.last_name:
            full_name += self.last_name + " "
        return full_name.strip()

    class Meta:
        permissions = [
            ("approve_employee", "Can approve Employee"),
            ("terminate_employee", "Can terminate Employee"),
            ("assign_employee", "Can assign Project"),
            ("can_change_user_group", "Can change user group"),
            ("can_approve_payroll_summary", "Can approve payroll summary")
        ]

    def __str__(self):
        return self.get_full_name()


class CostCentre(models.Model):
    cost_centre = models.CharField(max_length=15)
    description = models.CharField(max_length=100, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('users:cost-centre-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.cost_centre


class Category(models.Model):
    name = models.CharField(max_length=50)

    def get_absolute_url(self):
        return reverse('users:category_list')

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True, editable=False)
    user_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    marital_status = models.CharField(max_length=9, choices=MARITAL_STATUS, null=True)
    image = models.ImageField(default='default.png', upload_to=get_image_filename, blank=True, null=True)
    mobile_number = models.CharField('Mobile No.', max_length=50, null=True, blank=True)
    date_of_birth = models.DateField('D.O.B', default=timezone.now, null=True)
    sex = models.CharField(max_length=6, choices=GENDER, null=True)
    id_number = models.CharField('ID No.', max_length=200, null=True, db_index=True)
    passport_number = models.CharField('Passport No.', max_length=200, blank=True, null=True)
    home_address = models.CharField(max_length=200, blank=True, null=True)
    residential_address = models.CharField(max_length=200, blank=True, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='State')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    tin_number = models.CharField('PIT/TIN', max_length=200, null=True, blank=True)
    nationality = models.ForeignKey('support_data.Nationality', on_delete=models.SET_NULL, null=True,
                                    related_name='employee_nationality')
    grade = models.ForeignKey('support_data.Grade', on_delete=models.SET_NULL, null=True, blank=True)
    duty_station = models.ForeignKey('support_data.DutyStation', on_delete=models.SET_NULL, null=True, blank=True)
    duty_country = models.ForeignKey('support_data.Country', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('support_data.Department', on_delete=models.SET_NULL, null=True, blank=True)
    job_title = models.ForeignKey('support_data.JobTitle', on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Job Title')
    line_manager = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='reports_to', null=True,
                                     blank=True)
    contract_type = models.ForeignKey('support_data.ContractType', on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name='Contract Type')
    contract_expiry = models.DateField(null=True, blank=True)
    appointment_date = models.DateField(default=timezone.now, null=True, blank=True)
    social_security = models.CharField('Security Security', max_length=3, choices=YES_OR_NO_TYPES, null=True,
                                       blank=True, default=YES_OR_NO_TYPES[1][0])
    payroll_center = models.ForeignKey('payroll.PayrollCenter', on_delete=models.SET_NULL, null=True)
    bank_1 = models.ForeignKey('payroll.Bank', on_delete=models.SET_NULL, related_name='first_bank', null=True,
                               blank=True, verbose_name='Bank 1')
    bank_2 = models.ForeignKey('payroll.Bank', on_delete=models.SET_NULL, related_name='second_bank', null=True,
                               blank=True, verbose_name='Bank 2')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, )
    first_account_number = models.CharField('A/C No.1', max_length=200, null=True, blank=True)
    second_account_number = models.CharField('A/C No.2', max_length=200, null=True, blank=True)
    first_bank_percentage = models.IntegerField('Percentage', null=True, blank=True, default=0)
    second_bank_percentage = models.IntegerField('Percentage', null=True, blank=True, default=0)
    social_security_number = models.CharField('Social Security No.', max_length=200, null=True, blank=True)
    nhif_number = models.CharField('NSIF No.', max_length=200, null=True, blank=True)
    currency = models.ForeignKey('payroll.Currency', on_delete=models.SET_NULL, null=True, blank=True)
    cost_centre = models.ForeignKey('users.CostCentre', on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Cost Centre')

    PAYMENT_OPTIONS = (
        ('BANK', 'BANK'),
        ('CASH', 'CASH')
    )
    payment_type = models.CharField(choices=PAYMENT_OPTIONS, max_length=4, null=True, blank=True)
    INSURANCE_CATEGORIES = (
        ('M', 'M'),
        ('M+1', 'M+1'),
        ('M+2', 'M+2'),
        ('M+3', 'M+3'),
        ('M+4', 'M+4'),
        ('M+5', 'M+5'),
        ('M+6', 'M+6')
    )
    medical_insurance_category = models.CharField(choices=INSURANCE_CATEGORIES, null=True, blank=True, max_length=5)
    medical_insurance_number = models.CharField(max_length=200, null=True, blank=True,
                                                verbose_name='Medical Insurance No.')
    sos_name_1 = models.CharField('Emergency contact name', max_length=150, null=True, blank=True)
    sos_phone_number_1 = models.CharField('Emergency contact Phone No.', max_length=50, blank=True, null=True)
    sos_address_1 = models.CharField('Emergency contact address', max_length=250, null=True, blank=True)
    sos_relationship_1 = models.ForeignKey('support_data.Relationship', on_delete=models.SET_NULL, null=True,
                                           blank=True, verbose_name='Relationship', related_name='sos_relationship_1')
    sos_name_2 = models.CharField('Emergency contact name', max_length=150, null=True, blank=True)
    sos_phone_number_2 = models.CharField('Emergency contact Phone No.', max_length=50, blank=True, null=True)
    sos_address_2 = models.CharField('Emergency contact address', max_length=250, null=True, blank=True)
    sos_relationship_2 = models.ForeignKey('support_data.Relationship', on_delete=models.SET_NULL, null=True,
                                           blank=True, verbose_name='Relationship', related_name='sos_relationship_2')
    sos_name_3 = models.CharField('Emergency contact name', max_length=150, null=True, blank=True)
    sos_phone_number_3 = models.CharField('Emergency contact Phone No.', max_length=50, blank=True, null=True)
    sos_address_3 = models.CharField('Emergency contact address', max_length=250, null=True, blank=True)
    sos_relationship_3 = models.ForeignKey('support_data.Relationship', on_delete=models.SET_NULL, null=True,
                                           blank=True, verbose_name='Relationship', related_name='sos_relationship_3')
    transferable = models.CharField(max_length=3, choices=YES_OR_NO_TYPES, null=True, blank=True)
    kin_full_name = models.CharField('Full name', max_length=250, null=True, blank=True)
    kin_phone_number = models.CharField('Mobile numbers', max_length=100, blank=True, null=True)
    kin_relationship = models.ForeignKey('support_data.Relationship', on_delete=models.SET_NULL, null=True, blank=True,
                                         verbose_name='Relationship', related_name='kin_relationship')
    kin_nationality = models.ForeignKey('support_data.Nationality', on_delete=models.SET_NULL, null=True,
                                        verbose_name='Nationality', blank=True)
    kin_passport_number = models.CharField('Passport No.', max_length=200, blank=True, null=True)
    kin_address = models.CharField('Address', max_length=250, null=True, blank=True)
    employment_status = models.CharField(max_length=17, choices=EMP_STATUS, default=EMP_STATUS[0][0], blank=True,
                                         null=True, db_index=True)
    agresso_number = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    documents = models.FileField(upload_to=get_doc_filename, blank=True, null=True)
    payment_location = models.ForeignKey('support_data.DutyStation', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='payment_location')
    assigned_locations = models.ManyToManyField('support_data.DutyStation', related_name="assigned_locations",
                                                blank=True)

    def clean(self):
        if self.payroll_center is None:
            raise ValidationError("Payroll Canter required.")

        if self.basic_salary is None:
            raise ValidationError("Basic salary required.")

        # TODO: FIND OUT IF THESE VALIDATIONS ARE ACTUALLY NECESSARY
        # if self.first_bank_percentage > 0:
        #     if self.bank_1 is None:
        #         raise ValidationError("Bank 1 required.")
        #     if self.first_account_number is None:
        #         raise ValidationError("Account 1 required.")
        #
        # if self.second_bank_percentage > 0:
        #     if self.bank_2 is None:
        #         raise ValidationError("Bank 2 required.")
        #     if self.second_account_number is None:
        #         raise ValidationError("Account 2 required.")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.user}'


def round_decimal(value):
    if value is not None:
        return round(value)
    return value


class PayrollProcessors(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    earning_and_deductions_type = models.ForeignKey('payroll.EarningDeductionType', on_delete=models.PROTECT,
                                                    blank=True, null=True)
    earning_and_deductions_category = models.ForeignKey('payroll.EarningDeductionCategory',
                                                        on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, db_index=True)
    payroll_period = models.ForeignKey('payroll.PayrollPeriod', on_delete=models.SET_NULL, null=True, blank=True)
    payroll_key = models.CharField(max_length=250, blank=True, primary_key=True, unique=True, default=None,
                                   editable=False)

    def to_dict(self):
        data = {
            'payroll_key': self.payroll_key,
            'employee': self.employee,
            'earning_and_deductions_type': self.earning_and_deductions_type,
            'earning_and_deductions_category': self.earning_and_deductions_category,
            'amount': self.amount
        }
        return data

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.payroll_key is None:
            self.payroll_key = f'P{self.payroll_period_id}S{self.employee_id}K{self.earning_and_deductions_type_id}'

        self.amount = round_decimal(self.amount)

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.payroll_key}-{self.payroll_period.payroll_center}-{self.earning_and_deductions_type}'


class TerminatedEmployees(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True)
    notice_date = models.DateField(default=timezone.now, null=True, blank=True)
    exit_date = models.DateField(default=timezone.now, null=True, blank=True)
    days_given = models.PositiveIntegerField(null=True, blank=True)
    employable = models.CharField(max_length=3, choices=YES_OR_NO_TYPES, null=True, blank=True)
    reason_for_exit = models.ForeignKey('support_data.TerminationReason', on_delete=models.SET_NULL,
                                        null=True, blank=True, verbose_name='Reason')
    liked_most = models.TextField(null=True, blank=True,
                                  verbose_name='What did you like most about working here?')
    liked_least = models.TextField(null=True, blank=True,
                                   verbose_name='What did you like least about working here?')
    change = models.TextField(null=True, blank=True,
                              verbose_name='If you could change anything about this organization/your department what would it be?')
    recommend_org = models.CharField(choices=YES_OR_NO_TYPES, max_length=3, null=True, blank=True)
    reason_for_no = models.TextField(null=True, blank=True)
    reason_for_coming_back = models.TextField(null=True, blank=True)
    RATINGS = (
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
    )
    rating = models.CharField(choices=RATINGS, max_length=3, verbose_name='Rate the organization', null=True)

    def __str__(self):
        return f'{self.employee}'


class Project(models.Model):
    project_code = models.CharField(max_length=20)
    project_name = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse('users:project-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.project_code


class SOF(models.Model):
    sof_code = models.CharField(max_length=20)
    sof_name = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse('users:sof-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.sof_code


class DEA(models.Model):
    dea_code = models.CharField(max_length=20)
    dea_name = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse('users:dea-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.dea_code


class EmployeeProject(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    cost_center = models.ForeignKey(CostCentre, on_delete=models.SET_NULL, null=True)
    project_code = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    sof_code = models.ForeignKey(SOF, on_delete=models.SET_NULL, null=True)
    dea_code = models.ForeignKey(DEA, on_delete=models.SET_NULL, null=True)
    contribution_percentage = models.IntegerField(default=100)

    def get_absolute_url(self):
        return reverse('users:employee-assign-project')

    def clean(self):
        # validate contribution_percentage
        # to determine that no project assignment is made beyond 100% contribution per employee
        projects = EmployeeProject.objects.filter(employee=self.employee, cost_center=self.cost_center_id,
                                                  project_code=self.project_code_id, sof_code=self.sof_code_id,
                                                  dea_code=self.dea_code_id)
        if projects.exists():
            total_contrib = 0
            for project in projects.iterator():
                total_contrib += project.contribution_percentage

            total_contrib += self.contribution_percentage
            if total_contrib > 100:
                total_contrib -= self.contribution_percentage
                available_contrib = 100 - total_contrib

                if available_contrib == 0:
                    raise ValidationError('No more assignments can be made to this project for this employee.')
                else:
                    raise ValidationError(f'Only {available_contrib}% contribution can be \
                     add to this project for this employee')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.employee} project'


class EmployeeMovement(models.Model):
    OVERTIME = (
        ("NORMAL", "Normal"),
        ("WEEKEND", "Weekend"),
    )

    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, editable=False)
    employee_name = models.CharField(max_length=300, null=True, blank=True)
    department = models.CharField(max_length=300, null=True, blank=True)
    job_title = models.CharField(max_length=300, null=True, blank=True)
    parameter = models.ForeignKey('support_data.MovementParameter', on_delete=models.PROTECT)
    earnings = models.ForeignKey('payroll.EarningDeductionType', on_delete=models.DO_NOTHING, null=True, blank=True)
    payroll_period = models.ForeignKey('payroll.PayrollPeriod', on_delete=models.DO_NOTHING, null=True, blank=True)
    hours = models.FloatField(null=True, blank=True)
    over_time_category = models.CharField(max_length=10, choices=OVERTIME, null=True, blank=True)
    move_from = models.CharField(max_length=150, null=True, blank=True)
    move_to = models.CharField(max_length=150, null=True, blank=True)
    date = models.DateField(auto_now=True)
    remarks = models.CharField(max_length=400, null=True, blank=True)
    status = models.CharField(max_length=20, blank=True, editable=False, default='SHOW')
    movement_requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)

    def __str__(self):
        return f'{self.parameter.name.capitalize()} Movement for {self.employee_name}'


class PayrollProcessorManager(models.Model):
    payroll_period = models.OneToOneField('payroll.PayrollPeriod', on_delete=models.CASCADE, primary_key=True)
    processed_status = models.CharField(max_length=3, default='NO')
    number_of_approvers = models.IntegerField(default=0)
