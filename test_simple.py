#!/usr/bin/env python
"""
Simple test after cache clearing
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

def test_simple():
    """Simple test all components"""
    
    print("=== TESTING AFTER CACHE CLEAR ===")
    
    # 1. Test URL resolution
    print("\n1. Testing URL resolution:")
    try:
        from django.urls import reverse
        urls_to_test = [
            'patients:list',
            'patients:create',
            'accounts:set_language',
            'dashboard:index',
        ]
        
        for url_name in urls_to_test:
            try:
                resolved = reverse(url_name)
                print(f"  [OK] {url_name} -> {resolved}")  
            except Exception as e:
                print(f"  [ERROR] {url_name} -> {e}")
                
    except Exception as e:
        print(f"  [ERROR] URL resolution failed: {e}")
    
    # 2. Test context processors
    print("\n2. Testing context processors:")
    try:
        from accounts.context_processors import language_context
        print("  [OK] language_context imported")
        
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {'django_language': 'es'}
        
        context = language_context(request)
        print(f"  [OK] Context keys: {list(context.keys())}")
            
    except Exception as e:
        print(f"  [ERROR] Context processor failed: {e}")
    
    # 3. Test views
    print("\n3. Testing views:")
    try:
        from accounts.views_lang import set_language
        print("  [OK] set_language view imported")
        
        from patients.views import patient_list
        print("  [OK] patient_list view imported")
        
    except Exception as e:
        print(f"  [ERROR] Views failed: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == '__main__':
    test_simple()