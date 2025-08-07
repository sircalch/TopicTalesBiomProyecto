#!/usr/bin/env python
"""
Test template rendering with URL resolution
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.template import Template, Context
from django.contrib.auth import get_user_model
from django.template.loader import get_template

User = get_user_model()

def test_template_urls():
    """Test URL resolution in template"""
    
    # Test simple URL resolution
    template_content = """
    Testing URL resolution:
    {% load static %}
    
    1. Basic patients URL: {% url 'patients:list' %}
    2. Export Excel URL: {% url 'patients:export_excel' %}
    3. Export PDF URL: {% url 'patients:export_pdf' %}  
    4. Export CSV URL: {% url 'patients:export_csv' %}
    """
    
    try:
        template = Template(template_content)
        context = Context({})
        
        rendered = template.render(context)
        print("Template rendered successfully:")
        print(rendered)
        
    except Exception as e:
        print(f"Template rendering failed: {e}")
        import traceback
        traceback.print_exc()

def test_patients_template():
    """Test the actual patients template"""
    
    try:
        # Get the actual template
        template = get_template('patients/list.html')
        
        # Create minimal context
        user = User.objects.get(username='test_nav_user')
        context = {
            'user': user,
            'total_patients': 0,
            'new_this_month': 0,
            'active_patients': 0,
            'with_appointments_today': 0,
            'patients': [],
        }
        
        # Try to render
        rendered = template.render(context)
        print("Patients template rendered successfully")
        print(f"Template length: {len(rendered)} characters")
        
        # Check for export URLs
        if '/patients/export/excel/' in rendered:
            print("[OK] export excel URL found in rendered template")
        else:
            print("[ERROR] export excel URL NOT found in rendered template")
            
        if 'patients:export_excel' in rendered:
            print("[OK] export_excel template tag found")
        else:
            print("[ERROR] export_excel template tag NOT found")
            
        # Let's also look for the dropdown menu
        if 'dropdown-menu' in rendered:
            print("[OK] dropdown menu found")
        else:
            print("[ERROR] dropdown menu NOT found")
            
        # Search for the export button
        if 'Exportar' in rendered:
            print("[OK] Export button text found")
        else:
            print("[ERROR] Export button text NOT found")
            
    except Exception as e:
        print(f"Patients template rendering failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 50)
    print("Testing URL Resolution in Templates")
    print("=" * 50)
    
    test_template_urls()
    
    print("\n" + "=" * 50)
    print("Testing Patients Template")
    print("=" * 50)
    
    test_patients_template()