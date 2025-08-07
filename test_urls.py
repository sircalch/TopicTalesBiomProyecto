#!/usr/bin/env python
"""
Test URL resolution for patients app
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

def test_patient_urls():
    """Test patient URL resolution"""
    
    urls_to_test = [
        'patients:list',
        'patients:create',
        'patients:search',
        'patients:export_excel',
        'patients:export_pdf', 
        'patients:export_csv',
        'patients:quick_actions'
    ]
    
    print("Testing Patient URLs...")
    print("=" * 40)
    
    for url_name in urls_to_test:
        try:
            resolved_url = reverse(url_name)
            print(f"[OK] {url_name} -> {resolved_url}")
        except NoReverseMatch as e:
            print(f"[ERROR] {url_name} -> ERROR: {e}")
    
    # Test URLs with parameters
    param_urls = [
        ('patients:detail', {'patient_id': 1}),
        ('patients:edit', {'patient_id': 1}),
        ('patients:medical_history', {'patient_id': 1}),
        ('patients:vital_signs', {'patient_id': 1}),
        ('patients:documents', {'patient_id': 1}),
    ]
    
    print("\nTesting URLs with parameters...")
    print("=" * 40)
    
    for url_name, kwargs in param_urls:
        try:
            resolved_url = reverse(url_name, kwargs=kwargs)
            print(f"[OK] {url_name} -> {resolved_url}")
        except NoReverseMatch as e:
            print(f"[ERROR] {url_name} -> ERROR: {e}")

if __name__ == '__main__':
    test_patient_urls()