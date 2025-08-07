#!/usr/bin/env python
"""
Test patients page specifically
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

def test_patients_page():
    """Test accessing the patients page"""
    
    client = Client()
    
    # Try to access patients page without authentication
    print("Testing patients page access...")
    
    try:
        # Get test user
        user = User.objects.get(username='test_nav_user')
        client.force_login(user)
        
        # Access the page
        response = client.get('/patients/')
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("[OK] Patients page loaded successfully")
        elif response.status_code == 302:
            print(f"[REDIRECT] Redirecting to: {response.url}")
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            
        # Check if it's a template error
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if 'NoReverseMatch' in content:
                print("[ERROR] NoReverseMatch found in response")
                # Find the specific error
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'NoReverseMatch' in line or 'export_excel' in line:
                        print(f"Error context: {line.strip()}")
            elif 'export_excel' in content:
                print("[OK] export_excel found in template")
            else:
                print("[INFO] No export_excel references found")
                
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_patients_page()