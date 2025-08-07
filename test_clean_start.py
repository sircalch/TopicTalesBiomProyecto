#!/usr/bin/env python
"""
Test clean startup after cache clearing
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

def test_clean_startup():
    """Test all components after cache clearing"""
    
    print("=== TESTING CLEAN STARTUP ===")
    
    # 1. Test URL resolution
    print("\n1. Testing URL resolution:")
    try:
        from django.urls import reverse
        urls_to_test = [
            ('patients:list', '/patients/'),
            ('patients:create', '/patients/create/'),
            ('accounts:set_language', '/accounts/set-language/'),
            ('dashboard:index', '/dashboard/'),
        ]
        
        for url_name, expected in urls_to_test:
            try:
                resolved = reverse(url_name)
                if resolved == expected:
                    print(f"  ✅ {url_name} -> {resolved}")  
                else:
                    print(f"  ⚠️ {url_name} -> {resolved} (expected {expected})")
            except Exception as e:
                print(f"  ❌ {url_name} -> ERROR: {e}")
                
    except Exception as e:
        print(f"  ❌ URL resolution failed: {e}")
    
    # 2. Test context processors
    print("\n2. Testing context processors:")
    try:
        from accounts.context_processors import language_context
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {'django_language': 'es'}
        
        context = language_context(request)
        
        if 'current_language' in context:
            print(f"  ✅ Language context: {context['current_language']}")
        else:
            print("  ❌ Language context missing")
            
        if 'translations' in context:
            print(f"  ✅ Translations available: {len(context['translations'])} entries")
        else:
            print("  ❌ Translations missing")
            
    except Exception as e:
        print(f"  ❌ Context processor failed: {e}")
    
    # 3. Test language switching view
    print("\n3. Testing language switching:")
    try:
        from accounts.views_lang import set_language
        print("  ✅ set_language view imported successfully")
    except Exception as e:
        print(f"  ❌ Language view import failed: {e}")
    
    # 4. Test template loading
    print("\n4. Testing template loading:")
    try:
        from django.template.loader import get_template
        templates_to_test = [
            'dashboard/index.html',
            'patients/list.html',
            'components/navbar.html'
        ]
        
        for template_name in templates_to_test:
            try:
                template = get_template(template_name)
                print(f"  ✅ {template_name} loaded")
            except Exception as e:
                print(f"  ❌ {template_name} failed: {e}")
                
    except Exception as e:
        print(f"  ❌ Template loading failed: {e}")
    
    print("\n=== CLEANUP TEST COMPLETE ===")

if __name__ == '__main__':
    test_clean_startup()