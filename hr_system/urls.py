"""hr_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from users import views

admin.AdminSite.site_header = 'Payroll System Administration'
admin.AdminSite.site_title = 'Payroll System Admin'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('logout_reset/', auth_views.LogoutView.as_view(next_page=settings.LOGOUT_RESET_REDIRECT_URL), name='reset_logout'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='users/auth/password_reset.html',
                                              email_template_name='users/auth/password_reset_email.html'),
         name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/auth/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/auth/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/auth/password_reset_complete.html'),
         name='password_reset_complete'),
    path('', include('payroll.urls')),
    path('users/', include('users.urls')),
    path('support_data/', include('support_data.urls')),
    path('admin/', views.login_admin),
    path('admin/payroll/', admin.site.urls),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
