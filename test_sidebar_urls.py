#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

print("=== Verificación de URLs del Sidebar ===")

# URLs principales del sidebar
sidebar_urls = [
    'dashboard:index',
    'patients:list',
    'patients:create', 
    'patients:search',
    'appointments:calendar',
    'appointments:list',
    'appointments:create',
    'medical_records:index',
    'medical_records:all_consultations',
    'medical_records:search',
    'psychology:dashboard',
    'psychology:evaluation_list',
    'psychology:session_list',
    'psychology:treatment_plan_list',
    'psychology:test_list',
    'nutrition:dashboard',
    'nutrition:assessment_list',
    'nutrition:diet_plan_list',
    'nutrition:consultation_list',
    'billing:index',
    'billing:invoices',
    'billing:create_invoice',
    'billing:payments',
    'billing:services',
    'equipment:list',
    'equipment:create',
    'accounts:users',
    'accounts:create_user',
    'accounts:organization',
    'accounts:profile',
    'accounts:subscription',
    'reports:index',
    'accounts:logout'
]

working_urls = []
broken_urls = []
missing_urls = []

for url_name in sidebar_urls:
    try:
        url = reverse(url_name)
        working_urls.append((url_name, url))
        print(f"✓ {url_name} -> {url}")
    except NoReverseMatch as e:
        broken_urls.append((url_name, str(e)))
        print(f"✗ {url_name} -> ERROR: {e}")
    except Exception as e:
        missing_urls.append((url_name, str(e)))
        print(f"? {url_name} -> UNKNOWN ERROR: {e}")

print(f"\n=== Resumen ===")
print(f"URLs funcionando: {len(working_urls)}")
print(f"URLs con errores: {len(broken_urls)}")
print(f"URLs con problemas: {len(missing_urls)}")

if broken_urls:
    print(f"\n=== URLs que necesitan corrección ===")
    for url_name, error in broken_urls:
        print(f"- {url_name}: {error}")

print(f"\n=== Estado del Sidebar: {'OK' if len(broken_urls) == 0 else 'NECESITA CORRECCIÓN'} ===")