from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.views.main import ChangeList

from users.forms import ProfileUpdateForm

from .models import User, Employee

# class EmployeeInline(admin.TabularInline):
#     model = Employee


# class CustomUserAdmin(UserAdmin):
#     inlines = [
#         EmployeeInline,
#     ]


admin.site.register(User, UserAdmin)


class EmployeeChangeList(ChangeList):

    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields,
                 list_select_related, list_per_page, list_max_show_all, list_editable, model_admin, sortable_by):
        super().__init__(request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields,
                         list_select_related, list_per_page, list_max_show_all, list_editable, model_admin, sortable_by)

        self.list_display = ['user', 'user_group', 'date_of_birth', 'job_title', 'appointment_date', ]
        self.list_display_links = ['user']
        self.list_editable = ['assigned_locations']


class EmployeeAdmin(admin.ModelAdmin):
    list_per_page = 10
    ordering = ['user']
    list_select_related = ['user']
    search_fields = ['user__first_name', 'user__middle_name', 'user__last_name', 'user__username']

    def get_changelist(self, request, **kwargs):
        return EmployeeChangeList

    def get_changelist_form(self, request, **kwargs):
        return ProfileUpdateForm


admin.site.register(Employee, EmployeeAdmin)
