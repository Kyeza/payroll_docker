from __future__ import absolute_import, unicode_literals

from .celery import app as celery_app

# This will make sure our Celery app is important every time Django starts.
__all__ = ['celery_app']