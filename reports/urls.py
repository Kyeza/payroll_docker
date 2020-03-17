from django.urls import path, include

from . import views

app_name = 'reports'
urlpatterns = [
    path('summary_report/<int:pk>', views.display_summary_report, name='display-summary-report'),
    path('update_summary_report/<int:pp>/<int:user>', views.update_summary_report, name='update-summary-report'),
    path('generate_reports/', views.generate_reports, name='generate-reports'),
    path('reconciliation_report/', views.generate_reconciliation_report, name='generate_reconciliation_report'),
    path('generate_reports/<int:pp>/<int:user>', views.generate_payslip_report, name='generate-payslip'),
    path('email/payslips/', views.send_mass_mail, name='email-payslip'),
]
