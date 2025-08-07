#!/usr/bin/env python
"""
Test export functions after phone field fix
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_export_functions():
    """Test all export functions after fix"""
    
    print("=== TESTING EXPORT FUNCTIONS AFTER FIX ===")
    
    client = Client()
    
    try:
        # Get test user
        user = User.objects.get(username='test_nav_user')
        client.force_login(user)
        
        # Test export functions
        export_tests = [
            ('/patients/export/excel/', 'Excel Export'),
            ('/patients/export/pdf/', 'PDF Export'),
            ('/patients/export/csv/', 'CSV Export'),
        ]
        
        for url, name in export_tests:
            try:
                print(f"\nTesting {name}:")
                response = client.get(url)
                
                if response.status_code == 200:
                    print(f"  [OK] {name}: Status 200")
                    if hasattr(response, 'content'):
                        content_length = len(response.content)
                        print(f"  [OK] Content length: {content_length} bytes")
                else:
                    print(f"  [ERROR] {name}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")
        
        # Test patient model field directly
        print(f"\nTesting Patient model:")
        from patients.models import Patient
        
        patients = Patient.objects.all()[:1]
        if patients:
            patient = patients[0]
            try:
                phone = patient.phone_number
                print(f"  [OK] patient.phone_number: '{phone}'")
            except AttributeError as e:
                print(f"  [ERROR] patient.phone_number: {e}")
                
            try:
                # This should fail
                phone = patient.phone
                print(f"  [WARNING] patient.phone still accessible: '{phone}'")
            except AttributeError:
                print(f"  [OK] patient.phone correctly raises AttributeError")
        else:
            print("  [INFO] No patients in database")
        
        print("\n=== EXPORT TEST COMPLETE ===")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_export_functions()