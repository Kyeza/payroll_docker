from django.db.models.signals import post_save
from django.dispatch import receiver

from payroll.models import PayrollPeriod
from users.models import PayrollProcessorManager


@receiver(post_save, sender=PayrollPeriod)
def create_processor_manager(sender, instance, created, **kwargs):
    if created:
        PayrollProcessorManager.objects.create(payroll_period=instance)


@receiver(post_save, sender=PayrollPeriod)
def save_processor_manager(sender, instance, **kwargs):
    instance.payrollprocessormanager.save()
