#!/usr/bin/env python
"""
Test export functions directly
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_export_functions():
    """Test export functions directly"""
    
    client = Client()
    
    try:
        # Get test user and login
        user = User.objects.get(username='test_nav_user')
        client.force_login(user)
        
        # Test each export function
        export_urls = [
            ('/patients/export/excel/', 'Excel Export'),
            ('/patients/export/pdf/', 'PDF Export'),
            ('/patients/export/csv/', 'CSV Export'),
        ]
        
        for url, name in export_urls:
            print(f"Testing {name}: {url}")
            try:
                response = client.get(url)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  [OK] {name} working")
                elif response.status_code == 302:
                    print(f"  [REDIRECT] {name} redirecting to: {response.url}")
                else:
                    print(f"  [ERROR] {name} returned {response.status_code}")
                    
            except Exception as e:
                print(f"  [ERROR] {name} exception: {e}")
        
        print("\n" + "="*50)
        print("Testing main patients page...")
        
        response = client.get('/patients/')
        print(f"Patients page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if '/patients/export/excel/' in content:
                print("[OK] Export URLs found in patients page")
            else:
                print("[ERROR] Export URLs NOT found in patients page")
                
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_export_functions()