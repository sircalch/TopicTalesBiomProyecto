#!/usr/bin/env python
"""
Force reload all modules and test again
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

# Force reload of patients app
import importlib
import patients.urls
import patients.views

importlib.reload(patients.urls)
importlib.reload(patients.views)

from django.urls import clear_url_caches
clear_url_caches()

print("Modules reloaded and URL caches cleared")

# Test URL resolution again
from django.urls import reverse
try:
    print('Testing after reload...')
    print('patients:export_excel ->', reverse('patients:export_excel'))
    print('[OK] URL resolution working after reload')
except Exception as e:
    print(f'[ERROR] Still failing after reload: {e}')

# Test with request
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

try:
    user = User.objects.get(username='test_nav_user')
    client = Client()
    client.force_login(user)
    
    response = client.get('/patients/')
    print(f'Patient page status after reload: {response.status_code}')
    
    if response.status_code == 200:
        print('[OK] Page accessible after reload')
    else:
        print(f'[ERROR] Page still failing: {response.status_code}')
        
except Exception as e:
    print(f'[ERROR] Page test failed: {e}')