"""
WSGI config for hr_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append('C:/Users/Administrator.SCI/Bitnami Django Stack projects/hr_system')
os.environ.setdefault("PYTHON_EGG_CACHE", "C:/Users/Administrator.SCI/Bitnami Django Stack projects/hr_system/egg_cache")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')

application = get_wsgi_application()

