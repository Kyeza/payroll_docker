from django.urls import path

from . import views
from .views import RecruitedEmployeeListView, ApprovedEmployeeListView, \
    SeparatedEmployeesListView, RejectedEmployeeListView, EmployeeBirthdayList, AssignProjectListView, \
    CostCentreCreate, CostCentreUpdate, CostCentreDetailView, CostCentreListView, \
    SOFCreate, SOFUpdate, SOFDetailView, \
    SOFListView, DEACreate, DEAUpdate, DEADetailView, DEAListView, EmployeeProjectsListView, \
    EmployeeProjectsDetailView, CategoryCreateView, CategoryDetailView, CategoryUpdateView, CategoryListView, \
    ProjectCreate, ProjectUpdate, ProjectDetailView, ProjectListView, EmployeeProjectCreation, \
    ChangeGroupEmployeeListView, EmployeeMovementsListView, EmployeeMovementsCreate, ApprovedEmployeeMovementsListView, \
    EnumerationsMovementsCreate, EnumEmployeeMovementsListView

app_name = 'users'
urlpatterns = [
    path('new_employee/', views.register_employee, name='new-employee'),
    path('profile/', views.profile, name='user-profile'),
    path('<int:pk>/edit_employee/', views.user_update_profile, name='user-detail'),
    path('new_employee_approval/', RecruitedEmployeeListView.as_view(), name='employee-approval'),
    path('edit_employee/',
         ApprovedEmployeeListView.as_view(template_name='users/employees/_approved_employee_list.html'),
         name='edit-employee'),
    path('terminate_employee/',
         ApprovedEmployeeListView.as_view(template_name='users/employees/_terminate_employee_list.html'),
         name='terminate-employee-list'),
    path('separated_employees/', SeparatedEmployeesListView.as_view(), name='separated-employee'),
    path('rejected_employees/', RejectedEmployeeListView.as_view(), name='rejected-employee-list'),
    path('employees_birthdays/', EmployeeBirthdayList.as_view(), name='employee-birthday-list'),
    path('reject_employee/<int:pk>/', views.reject_employee, name='reject-employee'),
    path('new_employee_approval/<int:pk>/edit/', views.approve_employee, name='approve-employee'),
    path('payroll_period/<int:pk>/process/', views.process_payroll_period, name='process_payroll-period'),
    path('payroll_period/<int:pk>/process/<int:user>', views.process_payroll_period, name='process_payroll-period'),
    path('terminate_employee/<int:pk>/', views.terminate_employee, name='terminate-employee'),
    path('employee/assign/projects/', AssignProjectListView.as_view(), name='employee-assign-project'),
    path('employee/assign/project/<int:pk>/', EmployeeProjectCreation.as_view(), name='employee-project-creation'),
    path('cost_centres/add/', CostCentreCreate.as_view(), name='cost-centre-create'),
    path('cost_centre/<int:pk>/edit/', CostCentreUpdate.as_view(), name='cost-centre-update'),
    path('cost_centres/', CostCentreListView.as_view(), name='cost-centre-list'),
    path('cost_centre/<int:pk>/', CostCentreDetailView.as_view(), name='cost-centre-detail'),
    path('projects/add/', ProjectCreate.as_view(), name='project-create'),
    path('project/<int:pk>/edit/', ProjectUpdate.as_view(), name='project-update'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('sof/add/', SOFCreate.as_view(), name='sof-create'),
    path('sof/<int:pk>/edit/', SOFUpdate.as_view(), name='sof-update'),
    path('sof/', SOFListView.as_view(), name='sof-list'),
    path('sof/<int:pk>/', SOFDetailView.as_view(), name='sof-detail'),
    path('dea/add/', DEACreate.as_view(), name='dea-create'),
    path('dea/<int:pk>/edit/', DEAUpdate.as_view(), name='dea-update'),
    path('dea/', DEAListView.as_view(), name='dea-list'),
    path('dea/<int:pk>/', DEADetailView.as_view(), name='dea-detail'),
    path('employee/projects/', EmployeeProjectsListView.as_view(), name='employee-project-list'),
    path('employee/project/<int:pk>', EmployeeProjectsDetailView.as_view(), name='employee-project-detail'),
    path('employee_category/add/', CategoryCreateView.as_view(), name='category_create'),
    path('employee_category/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_update'),
    path('employee_categories/', CategoryListView.as_view(), name='category_list'),
    path('employee_category/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('change_user_group/<int:pk>', views.user_change_group, name='user_change_group'),
    path('change/group/', ChangeGroupEmployeeListView.as_view(), name='change_employee_user_group'),
    path('employee/reactivate/<int:pk>', views.reactivate_employee, name='reactivate_employee'),
    path('employee/', ApprovedEmployeeMovementsListView.as_view(), name='employee_movements'),
    path('employee/movements/', EmployeeMovementsListView.as_view(), name='employee_movements_changelist'),
    path('employee/movements/add/<int:user_id>/<int:requester_id>/', EmployeeMovementsCreate.as_view(), name='employee_movements_add'),
    path('ajax/load_movements/', views.load_movements, name='ajax_load_movements'),
    path('ajax/load_current_param/', views.load_current_param, name='ajax_load_current'),
    path('employee/earnings/movements/add/<int:user_id>/<int:requester_id>/', EnumerationsMovementsCreate.as_view(),
         name='employee_movements_add_enums'),
    path('employee/earning/movements/', EnumEmployeeMovementsListView.as_view(), name='employee_movements_enums'),
    path('ajax/load_earnings/amount/', views.load_earnings_current_amount, name='ajax_load_current_earning'),
    path('approve/movement/<int:movement_id>/', views.approve_employee_movement, name='approve_employee_movement'),
    path('decline/movement/<int:movement_id>/', views.decline_employee_movement, name='decline_employee_movement'),
    path('ajax/load_overtime_factor/factor/', views.load_overtime_factor, name='ajax_load_factor'),
]
