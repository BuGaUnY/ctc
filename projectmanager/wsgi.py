"""
WSGI config for projectmanager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Adjust the path if your settings file is not in the root directory
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.projectmanager.settings')

application = get_wsgi_application()