#!/usr/bin/env python
"""
Quickly creates a demo teacher account.
Use during demos and initial Pro setup.
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.contrib.auth.models import User

u, created = User.objects.get_or_create(username='pro_demo', defaults={'is_staff': True})
if created:
    u.set_password('demo2026')
    u.save()
    print("Created pro_demo / demo2026")
else:
    print("Demo teacher already exists")
