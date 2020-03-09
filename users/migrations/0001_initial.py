# Generated by Django 2.2 on 2020-03-06 09:38

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('support_data', '0001_initial'),
        ('payroll', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'permissions': [('approve_employee', 'Can approve Employee'), ('terminate_employee', 'Can terminate Employee'), ('assign_employee', 'Can assign Project'), ('can_change_user_group', 'Can change user group'), ('can_approve_payroll_summary', 'Can approve payroll summary')],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CostCentre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost_centre', models.CharField(max_length=15)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DEA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dea_code', models.CharField(max_length=20)),
                ('dea_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='PayrollProcessorManager',
            fields=[
                ('payroll_period', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='payroll.PayrollPeriod')),
                ('processed_status', models.CharField(default='NO', max_length=3)),
                ('number_of_approvers', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_code', models.CharField(max_length=20)),
                ('project_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='SOF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sof_code', models.CharField(max_length=20)),
                ('sof_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('user', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('marital_status', models.CharField(choices=[('SINGLE', 'Single'), ('MARRIED', 'Married'), ('SEPARATED', 'Separated'), ('DIVORCED', 'Divorced'), ('WIDOWER', 'Widower')], max_length=9, null=True)),
                ('image', models.ImageField(blank=True, default='default.png', null=True, upload_to=users.utils.get_image_filename)),
                ('mobile_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='Mobile No.')),
                ('date_of_birth', models.DateField(default=django.utils.timezone.now, null=True, verbose_name='D.O.B')),
                ('sex', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], max_length=6, null=True)),
                ('id_number', models.CharField(db_index=True, max_length=200, null=True, verbose_name='ID No.')),
                ('passport_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='Passport No.')),
                ('home_address', models.CharField(blank=True, max_length=200, null=True)),
                ('residential_address', models.CharField(blank=True, max_length=200, null=True)),
                ('basic_salary', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('tin_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='PIT/TIN')),
                ('contract_expiry', models.DateField(blank=True, null=True)),
                ('appointment_date', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('social_security', models.CharField(blank=True, choices=[('YES', 'Yes'), ('NO', 'No')], default='NO', max_length=3, null=True, verbose_name='Security Security')),
                ('first_account_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='A/C No.1')),
                ('second_account_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='A/C No.2')),
                ('first_bank_percentage', models.IntegerField(blank=True, default=0, null=True, verbose_name='Percentage')),
                ('second_bank_percentage', models.IntegerField(blank=True, default=0, null=True, verbose_name='Percentage')),
                ('social_security_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='Social Security No.')),
                ('nhif_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='NSIF No.')),
                ('payment_type', models.CharField(blank=True, choices=[('BANK', 'BANK'), ('CASH', 'CASH')], max_length=4, null=True)),
                ('medical_insurance_category', models.CharField(blank=True, choices=[('M', 'M'), ('M+1', 'M+1'), ('M+2', 'M+2'), ('M+3', 'M+3'), ('M+4', 'M+4'), ('M+5', 'M+5'), ('M+6', 'M+6')], max_length=5, null=True)),
                ('medical_insurance_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='Medical Insurance No.')),
                ('sos_name_1', models.CharField(blank=True, max_length=150, null=True, verbose_name='Emergency contact name')),
                ('sos_phone_number_1', models.CharField(blank=True, max_length=50, null=True, verbose_name='Emergency contact Phone No.')),
                ('sos_address_1', models.CharField(blank=True, max_length=250, null=True, verbose_name='Emergency contact address')),
                ('sos_name_2', models.CharField(blank=True, max_length=150, null=True, verbose_name='Emergency contact name')),
                ('sos_phone_number_2', models.CharField(blank=True, max_length=50, null=True, verbose_name='Emergency contact Phone No.')),
                ('sos_address_2', models.CharField(blank=True, max_length=250, null=True, verbose_name='Emergency contact address')),
                ('sos_name_3', models.CharField(blank=True, max_length=150, null=True, verbose_name='Emergency contact name')),
                ('sos_phone_number_3', models.CharField(blank=True, max_length=50, null=True, verbose_name='Emergency contact Phone No.')),
                ('sos_address_3', models.CharField(blank=True, max_length=250, null=True, verbose_name='Emergency contact address')),
                ('transferable', models.CharField(blank=True, choices=[('YES', 'Yes'), ('NO', 'No')], max_length=3, null=True)),
                ('kin_full_name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Full name')),
                ('kin_phone_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='Mobile numbers')),
                ('kin_passport_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='Passport No.')),
                ('kin_address', models.CharField(blank=True, max_length=250, null=True, verbose_name='Address')),
                ('employment_status', models.CharField(blank=True, choices=[('RECRUIT', 'Recruit'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('TERMINATED', 'Terminated')], db_index=True, default='RECRUIT', max_length=17, null=True)),
                ('agresso_number', models.CharField(blank=True, db_index=True, max_length=200, null=True)),
                ('documents', models.FileField(blank=True, null=True, upload_to=users.utils.get_doc_filename)),
                ('assigned_locations', models.ManyToManyField(blank=True, related_name='assigned_locations', to='support_data.DutyStation')),
                ('bank_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='first_bank', to='payroll.Bank', verbose_name='Bank 1')),
                ('bank_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='second_bank', to='payroll.Bank', verbose_name='Bank 2')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.Category')),
                ('contract_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='support_data.ContractType', verbose_name='Contract Type')),
                ('cost_centre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.CostCentre', verbose_name='Cost Centre')),
                ('currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.Currency')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='support_data.Department')),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.District', verbose_name='State')),
                ('duty_country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='support_data.Country')),
                ('duty_station', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='support_data.DutyStation')),
                ('grade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='support_data.Grade')),
                ('job_title', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='support_data.JobTitle', verbose_name='Job Title')),
                ('kin_nationality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='support_data.Nationality', verbose_name='Nationality')),
                ('kin_relationship', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kin_relationship', to='support_data.Relationship', verbose_name='Relationship')),
                ('line_manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_to', to=settings.AUTH_USER_MODEL)),
                ('nationality', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_nationality', to='support_data.Nationality')),
                ('payment_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_location', to='support_data.DutyStation')),
                ('payroll_center', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.PayrollCenter')),
                ('sos_relationship_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sos_relationship_1', to='support_data.Relationship', verbose_name='Relationship')),
                ('sos_relationship_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sos_relationship_2', to='support_data.Relationship', verbose_name='Relationship')),
                ('sos_relationship_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sos_relationship_3', to='support_data.Relationship', verbose_name='Relationship')),
                ('user_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='PayrollProcessors',
            fields=[
                ('amount', models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=12, null=True)),
                ('payroll_key', models.CharField(blank=True, default=None, editable=False, max_length=250, primary_key=True, serialize=False, unique=True)),
                ('earning_and_deductions_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.EarningDeductionCategory')),
                ('earning_and_deductions_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='payroll.EarningDeductionType')),
                ('payroll_period', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.PayrollPeriod')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contribution_percentage', models.IntegerField(default=100)),
                ('cost_center', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.CostCentre')),
                ('dea_code', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.DEA')),
                ('project_code', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.Project')),
                ('sof_code', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.SOF')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeMovement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_name', models.CharField(blank=True, max_length=300, null=True)),
                ('department', models.CharField(blank=True, max_length=300, null=True)),
                ('job_title', models.CharField(blank=True, max_length=300, null=True)),
                ('hours', models.FloatField(blank=True, null=True)),
                ('over_time_category', models.CharField(blank=True, choices=[('NORMAL', 'Normal'), ('WEEKEND', 'Weekend')], max_length=10, null=True)),
                ('move_from', models.CharField(blank=True, max_length=150, null=True)),
                ('move_to', models.CharField(blank=True, max_length=150, null=True)),
                ('date', models.DateField(auto_now=True)),
                ('remarks', models.CharField(blank=True, max_length=400, null=True)),
                ('status', models.CharField(blank=True, default='SHOW', editable=False, max_length=20)),
                ('earnings', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='payroll.EarningDeductionType')),
                ('movement_requester', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('parameter', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='support_data.MovementParameter')),
                ('payroll_period', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='payroll.PayrollPeriod')),
                ('employee', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='TerminatedEmployees',
            fields=[
                ('employee', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='termination_report', serialize=False, to='users.Employee')),
                ('notice_date', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('exit_date', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('days_given', models.PositiveIntegerField(blank=True, null=True)),
                ('employable', models.CharField(blank=True, choices=[('YES', 'Yes'), ('NO', 'No')], max_length=3, null=True)),
                ('liked_most', models.TextField(blank=True, null=True, verbose_name='What did you like most about working here?')),
                ('liked_least', models.TextField(blank=True, null=True, verbose_name='What did you like least about working here?')),
                ('change', models.TextField(blank=True, null=True, verbose_name='If you could change anything about this organization/your department what would it be?')),
                ('recommend_org', models.CharField(blank=True, choices=[('YES', 'Yes'), ('NO', 'No')], max_length=3, null=True)),
                ('reason_for_no', models.TextField(blank=True, null=True)),
                ('reason_for_coming_back', models.TextField(blank=True, null=True)),
                ('rating', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], max_length=3, null=True, verbose_name='Rate the organization')),
                ('reason_for_exit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='support_data.TerminationReason', verbose_name='Reason')),
            ],
        ),
    ]
