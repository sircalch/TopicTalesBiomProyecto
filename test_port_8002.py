#!/usr/bin/env python
"""
Test URL resolution on port 8002
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_port_8002():
    """Test URL resolution and page access"""
    
    # Test URL resolution
    try:
        print('Testing URL resolution...')
        print('1. patients:list ->', reverse('patients:list'))
        print('2. patients:export_excel ->', reverse('patients:export_excel'))
        print('3. patients:export_pdf ->', reverse('patients:export_pdf'))
        print('4. patients:export_csv ->', reverse('patients:export_csv'))
        print('[OK] URL resolution working')
    except Exception as e:
        print(f'[ERROR] URL resolution failed: {e}')
        return

    # Test with user context
    try:
        user = User.objects.get(username='test_nav_user')
        client = Client()
        client.force_login(user)
        
        response = client.get('/patients/')
        print(f'Patient page status: {response.status_code}')
        
        if response.status_code != 200:
            print(f'[ERROR] Error accessing patients page: {response.status_code}')
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                if 'NoReverseMatch' in content:
                    print('[ERROR] NoReverseMatch found in response')
        else:
            print('[OK] Patient page accessible')
            
    except Exception as e:
        print(f'[ERROR] Page access failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_port_8002()