#!/usr/bin/env python
"""
Debug template rendering issue on port 8002
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.template.loader import render_to_string
from django.template import Context
from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()

def debug_template():
    """Debug the patients template rendering"""
    
    try:
        user = User.objects.get(username='test_nav_user')
        
        # Create a minimal context similar to the view
        context = {
            'user': user,
            'total_patients': 0,
            'new_this_month': 0,
            'active_patients': 0,
            'with_appointments_today': 0,
            'patients': [],
            'request': type('MockRequest', (), {
                'GET': {},
                'user': user
            })(),
        }
        
        print("Attempting to render patients/list.html template...")
        
        # Try to render the template
        rendered = render_to_string('patients/list.html', context)
        
        print(f"[OK] Template rendered successfully ({len(rendered)} chars)")
        
        # Check for the problematic URLs
        if 'patients:export_excel' in rendered:
            print("[OK] export_excel template tag found")
        else:
            print("[ERROR] export_excel template tag NOT found")
            
        if '/patients/export/excel/' in rendered:
            print("[OK] export excel URL found in rendered output")
        else:
            print("[ERROR] export excel URL NOT found in rendered output")
            
    except Exception as e:
        print(f"[ERROR] Template rendering failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_template()