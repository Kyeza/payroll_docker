# import datetime
#
# from django.test import TestCase, Client
# from django.urls import reverse
# from django.utils import timezone
# from users.models import User
#
# from payroll.models import PayrollCenter
# from support_data.models import Country, Nationality, Organization
# from users.forms import UserCreationForm, ProfileCreationForm
# from users.models import Employee
#
#
# class TestEmployeeRegistrationView(TestCase):
#
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user('test_user', 'testuser@email.com', 'testpassword')
#         self.client.login(username='test_user', password='testpassword')
#         self.registration_url = reverse('users:new-employee')
#         self.user_form = UserCreationForm()
#         self.profile_form = ProfileCreationForm()
#
#     def test_register_new_employee_get(self):
#         response = self.client.get(self.registration_url)
#
#         self.assertEquals(response.status_code, 200)
#
#     # def test_register_new_employee_post(self):
#     #     country = Country.objects.create(country_name='UGANDA', country_code='UG')
#     #     Nationality.objects.create(country_nationality='UGANDAN', country=country)
#     #     organization = Organization.objects.create(name='TEST ORG', country=country)
#     #     PayrollCenter.objects.create(name='TEST PAYROLL CENTER', date_create=timezone.now(), country=country,
#     #                                  organization=organization, description='no desc')
#     #     # print(f'user: {User.objects.first().usern}')
#     #     self.client.login(username='test_username', password='testpassword')
#     #     response = self.client.post(self.registration_url, data={'first_name': 'test_first_name',
#     #                                                              'middle_name': 'test_middle_name',
#     #                                                              'last_name': 'test_last_name',
#     #                                                              'date_of_birth': datetime.date.today,
#     #                                                              'sex': 'MALE',
#     #                                                              'marital_status': 'SINGLE',
#     #                                                              'email': 'test@email.com',
#     #                                                              'id_number': '001',
#     #                                                              'nationality': 'UGANDAN',
#     #                                                              'basic_salary': '1000000',
#     #                                                              'payroll_center': 'TEST PAYROLL CENTER'})
#     #
#     #     print(dir(response))
#     #     print(response.context)
#
#         # print(f'context: {response.context}')
#         # print(f'context data: {response.context_data}')
#
#         # number = Employee.objects.count()
#
#         # print(f'num: {number}')
#
#         # self.assertEquals(number, 1)
#         # self.assertEquals(response.status_code, 200)