from django.urls import path

from . import views
from .views import OrganizationCreate, OrganizationListView, OrganizationUpdate, OrganizationDetailView, \
    OrganizationDelete, TaxBracketCreate, TaxBracketUpdate, TaxBracketListView, TaxBracketDetailView, \
    CountryOriginCreate, CountryOriginUpdate, CountryOriginDetailView, CountryOriginListView, \
    NationalityCreate, NationalityUpdate, NationalityDetailView, NationalityListView, \
    DutyStationCreate, DutyStationUpdate, DutyStationDetailView, DutyStationListView, \
    DepartmentCreate, DepartmentUpdate, DepartmentDetailView, DepartmentListView, \
    JobTitleCreate, JobTitleUpdate, JobTitleDetailView, JobTitleListView, \
    ContractTypeCreate, ContractTypeUpdate, ContractTypeDetailView, ContractTypeListView, \
    GradeCreate, GradeUpdate, GradeDetailView, GradeListView, TerminationReasonCreateView, TerminationReasonUpdateView, \
    TerminationReasonListView

app_name = 'support_data'
urlpatterns = [
    path('organizations/add/', OrganizationCreate.as_view(), name='organization-create'),
    path('organization/<int:pk>/edit', OrganizationUpdate.as_view(), name='organization-update'),
    path('organizations/', OrganizationListView.as_view(), name='organization-list'),
    path('organization/<int:pk>/', OrganizationDetailView.as_view(), name='organization-detail'),
    path('organization/<int:pk>/delete/', OrganizationDelete.as_view(), name='organization-delete'),
    path('tax_brackets/add/', TaxBracketCreate.as_view(), name='tax-bracket-create'),
    path('tax_bracket<int:pk>/edit/', TaxBracketUpdate.as_view(), name='tax-bracket-update'),
    path('tax_brackets/', TaxBracketListView.as_view(), name='tax-bracket-list'),
    path('tax_bracket/<int:pk>/', TaxBracketDetailView.as_view(), name='tax-bracket-detail'),
    path('country_of_origin/add/', CountryOriginCreate.as_view(), name='country-create'),
    path('country_of_origin<int:pk>/edit/', CountryOriginUpdate.as_view(), name='country-update'),
    path('countries_of_origin/', CountryOriginListView.as_view(), name='country-list'),
    path('country_of_origin/<int:pk>/', CountryOriginDetailView.as_view(), name='country-detail'),
    path('nationalities/add/', NationalityCreate.as_view(), name='nationality-create'),
    path('nationality<int:pk>/edit/', NationalityUpdate.as_view(), name='nationality-update'),
    path('nationalities/', NationalityListView.as_view(), name='nationality-list'),
    path('nationality/<int:pk>/', NationalityDetailView.as_view(), name='nationality-detail'),
    path('duty_stations/add/', DutyStationCreate.as_view(), name='duty-station-create'),
    path('duty_station<int:pk>/edit/', DutyStationUpdate.as_view(), name='duty-station-update'),
    path('duty_stations/', DutyStationListView.as_view(), name='duty-station-list'),
    path('duty_station/<int:pk>/', DutyStationDetailView.as_view(), name='duty-station-detail'),
    path('departments/add/', DepartmentCreate.as_view(), name='department-create'),
    path('department<int:pk>/edit/', DepartmentUpdate.as_view(), name='department-update'),
    path('departments/', DepartmentListView.as_view(), name='department-list'),
    path('department/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    path('job_titles/add/', JobTitleCreate.as_view(), name='job-title-create'),
    path('job_title<int:pk>/edit/', JobTitleUpdate.as_view(), name='job-title-update'),
    path('job_titles/', JobTitleListView.as_view(), name='job-title-list'),
    path('job_title/<int:pk>/', JobTitleDetailView.as_view(), name='job-title-detail'),
    path('contract_types/add/', ContractTypeCreate.as_view(), name='contract-type-create'),
    path('contract_type<int:pk>/edit/', ContractTypeUpdate.as_view(), name='contract-type-update'),
    path('contract_types/', ContractTypeListView.as_view(), name='contract-type-list'),
    path('contract_type/<int:pk>/', ContractTypeDetailView.as_view(), name='contract-type-detail'),
    path('grades/add/', GradeCreate.as_view(), name='grade-create'),
    path('grade<int:pk>/edit/', GradeUpdate.as_view(), name='grade-update'),
    path('grades/', GradeListView.as_view(), name='grade-list'),
    path('grade/<int:pk>/', GradeDetailView.as_view(), name='grade-detail'),
    path('separation_reason/add/', TerminationReasonCreateView.as_view(), name='reason-create'),
    path('separation_reason<int:pk>/edit/', TerminationReasonUpdateView.as_view(), name='reason-update'),
    path('separation_reason/', TerminationReasonListView.as_view(), name='reason-list'),
    path('send_approval_request/<int:period_id>/', views.send_mail_to_approvers, name='request-approval'),
    path('approve_payroll/<int:period_id>/', views.sign_off_payroll_summary, name='approve_payroll'),
    path('decline_payroll/', views.decline_payroll_summary, name='decline_payroll'),
    path('check_approval_status/<int:period_id>/', views.checkout_for_approval_status, name='approval_status')
]
