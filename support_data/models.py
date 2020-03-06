import datetime

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse

from hr_system.constants import YES_OR_NO_TYPES
from .constants import TAX_YEAR_CHOICES
from payroll.models import EarningDeductionType
from users.models import User


class Country(models.Model):
    """docstring for Countries"""
    country_name = models.CharField(max_length=36)
    country_code = models.CharField(max_length=3)

    def get_absolute_url(self):
        return reverse('support_data:country-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.country_name


class Nationality(models.Model):
    """docstring for Nationality"""
    country = models.OneToOneField(Country, on_delete=models.CASCADE, primary_key=True)
    country_nationality = models.CharField(max_length=36)

    def get_absolute_url(self):
        return reverse('support_data:nationality-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.country_nationality


class DutyStation(models.Model):
    """docstring for DutyStation"""
    duty_station = models.CharField(max_length=30)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    earnings_type = models.ForeignKey(EarningDeductionType, on_delete=models.SET_NULL, null=True, blank=True)
    earning_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=150, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('support_data:duty-station-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.duty_station


class Department(models.Model):
    """docstring for Department"""
    department = models.CharField(max_length=100)
    description = models.CharField(max_length=300)

    def get_absolute_url(self):
        return reverse('support_data:department-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.department


class JobTitle(models.Model):
    """docstring for JobTitle"""
    job_title = models.CharField(max_length=200)
    description = models.CharField(max_length=150)

    def get_absolute_url(self):
        return reverse('support_data:job-title-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.job_title


class ContractType(models.Model):
    """docstring for ContractType"""
    contract_type = models.CharField(max_length=150, null=True, blank=True)
    contract_expiry = models.CharField(max_length=3, choices=YES_OR_NO_TYPES, null=True, blank=True)
    leave_entitled = models.CharField(max_length=3, choices=YES_OR_NO_TYPES, null=True, blank=True)
    leave_days_entitled = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(30)],
                                              null=True, blank=True)

    def get_absolute_url(self):
        return reverse('support_data:contract-type-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.contract_type


class Relationship(models.Model):
    """docstring for Relationship"""
    relationship = models.CharField(max_length=150)

    def __str__(self):
        return self.relationship


class Organization(models.Model):
    """docstring for Organization"""
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('support_data:organization-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Grade(models.Model):
    """docstring for Grade"""
    grade = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def get_absolute_url(self):
        return reverse('support_data:grade-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.grade


class Tax(models.Model):
    """docstring for Taxes"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    lower_boundary = models.DecimalField(max_digits=7, decimal_places=2)
    upper_boundary = models.DecimalField(max_digits=7, decimal_places=2)
    fixed_amount = models.DecimalField(max_digits=7, decimal_places=2)
    year = models.IntegerField(choices=TAX_YEAR_CHOICES, default=datetime.datetime.now().year)

    def get_absolute_url(self):
        return reverse('support_data:tax-bracket-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.country


class TerminationReason(models.Model):
    reason = models.CharField(max_length=350)

    def __str__(self):
        return self.reason


class MovementParameter(models.Model):
    name = models.CharField(max_length=300)
    choice = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class PayrollApprover (models.Model):
    approver = models.OneToOneField('users.User', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.approver}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        user_content_type = ContentType.objects.get_for_model(User, for_concrete_model=True)
        permission = Permission.objects.filter(content_type=user_content_type)\
            .filter(name='Can approve payroll summary').first()
        self.approver.user_permissions.add(permission)
        super().save(force_insert, force_update, using, update_fields)


class SudaneseTaxRates(models.Model):
    lower_ssp_bound = models.DecimalField(max_digits=12, decimal_places=2)
    upper_ssp_bound = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.FloatField()
    actual_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    actual_usd_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
