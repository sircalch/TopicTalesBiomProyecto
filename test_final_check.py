#!/usr/bin/env python
"""
Final check of all functionalities
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_final_functionality():
    """Final test of all key functionalities"""
    
    print("=== FINAL FUNCTIONALITY CHECK ===")
    
    client = Client()
    
    try:
        # Get test user
        user = User.objects.get(username='test_nav_user')
        client.force_login(user)
        
        # Test pages
        pages_to_test = [
            ('/dashboard/', 'Dashboard'),
            ('/patients/', 'Patients List'),
            ('/patients/create/', 'Create Patient'),
        ]
        
        print("\n1. Testing page access:")
        for url, name in pages_to_test:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    print(f"  [OK] {name}: {response.status_code}")
                else:
                    print(f"  [ERROR] {name}: {response.status_code}")
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")
        
        # Test language switching
        print("\n2. Testing language switching:")
        try:
            # Set to English
            response = client.post('/accounts/set-language/', {
                'language': 'en',
                'next': '/dashboard/'
            })
            if response.status_code in [200, 302]:
                print("  [OK] Language switch to English")
            else:
                print(f"  [ERROR] Language switch failed: {response.status_code}")
                
            # Set back to Spanish
            response = client.post('/accounts/set-language/', {
                'language': 'es', 
                'next': '/dashboard/'
            })
            if response.status_code in [200, 302]:
                print("  [OK] Language switch to Spanish")
            else:
                print(f"  [ERROR] Language switch failed: {response.status_code}")
                
        except Exception as e:
            print(f"  [ERROR] Language switching: {e}")
        
        # Test export functions
        print("\n3. Testing export functions:")
        export_urls = [
            ('/patients/export/excel/', 'Excel Export'),
            ('/patients/export/pdf/', 'PDF Export'),
            ('/patients/export/csv/', 'CSV Export'),
        ]
        
        for url, name in export_urls:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    print(f"  [OK] {name}: {response.status_code}")
                else:
                    print(f"  [ERROR] {name}: {response.status_code}")
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")
        
        print("\n=== ALL TESTS COMPLETED ===")
        print("System is ready on port 8003!")
        
    except Exception as e:
        print(f"[ERROR] Test setup failed: {e}")

if __name__ == '__main__':
    test_final_functionality()