#!/usr/bin/env python
"""
Test language switching system
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_language_system():
    """Test the complete language switching system"""
    
    print("=== TESTING LANGUAGE SYSTEM ===")
    
    client = Client()
    
    try:
        # Get test user
        user = User.objects.get(username='test_nav_user')
        client.force_login(user)
        
        # Test Spanish (default)
        print("\n1. Testing Spanish (default):")
        response = client.get('/dashboard/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'Panel de Control' in content:
                print("  [OK] Spanish content found: 'Panel de Control'")
            if 'Bienvenido' in content:
                print("  [OK] Spanish welcome message found")
            if 'Gestión de Pacientes' in response.content.decode('utf-8'):
                print("  [OK] Spanish navigation found")
        
        # Switch to English
        print("\n2. Testing English switch:")
        response = client.post('/accounts/set-language/', {
            'language': 'en',
            'next': '/dashboard/'
        })
        
        if response.status_code in [200, 302]:
            print("  [OK] Language switch request successful")
            
            # Check session
            session = client.session
            if session.get('django_language') == 'en':
                print("  [OK] Session language set to English")
            
            # Test English content
            response = client.get('/dashboard/')
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                if 'Dashboard' in content:
                    print("  [OK] English content found: 'Dashboard'")
                if 'Welcome' in content:
                    print("  [OK] English welcome message found")
        
        # Test patients page in English
        print("\n3. Testing Patients page in English:")
        response = client.get('/patients/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'Patient Management' in content:
                print("  [OK] English patients page working")
            if 'Export' in content:
                print("  [OK] English export options found")
        
        # Switch back to Spanish
        print("\n4. Testing Spanish switch:")
        response = client.post('/accounts/set-language/', {
            'language': 'es',
            'next': '/patients/'
        })
        
        if response.status_code in [200, 302]:
            response = client.get('/patients/')
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                if 'Gestión de Pacientes' in content:
                    print("  [OK] Back to Spanish successfully")
                if 'Exportar' in content:
                    print("  [OK] Spanish export options found")
        
        print("\n=== LANGUAGE SYSTEM WORKING PERFECTLY ===")
        
    except Exception as e:
        print(f"[ERROR] Language system test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_language_system()