#!/usr/bin/env python
"""
Live debug of the actual running server issue
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.urls import reverse, resolve, get_resolver
from django.conf import settings

def live_debug():
    """Debug the live server URL issue"""
    
    print("=== LIVE SERVER DEBUG ===")
    
    # 1. Check URL configuration
    print("\n1. Checking URL configuration:")
    try:
        resolver = get_resolver()
        print(f"Root URLconf: {settings.ROOT_URLCONF}")
        
        # Check if patients namespace exists
        namespace_dict = resolver.namespace_dict
        if 'patients' in namespace_dict:
            print("[OK] patients namespace found")
            
            # Get patients resolver
            patients_resolver = namespace_dict['patients'][1]
            print(f"Patients URL patterns: {len(patients_resolver.url_patterns)} patterns")
            
            # List all patterns
            for pattern in patients_resolver.url_patterns:
                print(f"  - {pattern.name}: {pattern.pattern}")
                
        else:
            print("[ERROR] patients namespace NOT found")
            
    except Exception as e:
        print(f"[ERROR] URL config check failed: {e}")
    
    # 2. Test URL reverse
    print("\n2. Testing URL reverse:")
    try:
        url = reverse('patients:export_excel')
        print(f"[OK] patients:export_excel -> {url}")
    except Exception as e:
        print(f"[ERROR] patients:export_excel failed: {e}")
    
    # 3. Check views
    print("\n3. Checking views:")
    try:
        import patients.views
        if hasattr(patients.views, 'export_patients_excel'):
            print("[OK] export_patients_excel view exists")
        else:
            print("[ERROR] export_patients_excel view NOT found")
            
        # List all view functions
        view_functions = [name for name in dir(patients.views) if not name.startswith('_')]
        print(f"Available views: {view_functions}")
        
    except Exception as e:
        print(f"[ERROR] Views check failed: {e}")
    
    # 4. Direct URL resolution test
    print("\n4. Direct URL resolution test:")
    try:
        resolved = resolve('/patients/export/excel/')
        print(f"[OK] /patients/export/excel/ resolves to: {resolved.func.__name__}")
        print(f"Namespace: {resolved.namespace}")
        print(f"URL name: {resolved.url_name}")
    except Exception as e:
        print(f"[ERROR] Direct resolution failed: {e}")
    
    # 5. Check if URL is actually registered
    print("\n5. Manual URL pattern check:")
    try:
        from patients.urls import urlpatterns
        print(f"patients.urls has {len(urlpatterns)} patterns:")
        for pattern in urlpatterns:
            if hasattr(pattern, 'name'):
                print(f"  - {pattern.name}: {pattern.pattern}")
    except Exception as e:
        print(f"[ERROR] Manual check failed: {e}")

if __name__ == '__main__':
    live_debug()