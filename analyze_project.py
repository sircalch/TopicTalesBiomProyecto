#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.apps import apps

print("=== ANÁLISIS COMPLETO DEL PROYECTO TOPICTALES BIOMÉDICA ===")

# 1. Análisis de apps instaladas
installed_apps = apps.get_app_configs()
topictales_apps = [app for app in installed_apps if not app.name.startswith('django') and not app.name in ['rest_framework', 'corsheaders', 'crispy_forms', 'crispy_bootstrap5', 'django_extensions']]

print(f"\n1. APLICACIONES TOPICTALES ({len(topictales_apps)}):")
for app in topictales_apps:
    print(f"   - {app.name}")

# 2. Análisis de modelos por app
print(f"\n2. MODELOS POR APLICACIÓN:")
for app in topictales_apps:
    models = list(app.get_models())
    print(f"   {app.name.upper()}: {len(models)} modelos")
    for model in models:
        print(f"     - {model.__name__}")

# 3. Análisis de URLs del sidebar
sidebar_urls = [
    'dashboard:index',
    'patients:list', 'patients:create', 'patients:search',
    'appointments:calendar', 'appointments:list', 'appointments:create',
    'medical_records:index', 'medical_records:all_consultations', 'medical_records:search',
    'psychology:dashboard', 'psychology:evaluation_list', 'psychology:session_list', 
    'psychology:treatment_plan_list', 'psychology:test_list',
    'nutrition:dashboard', 'nutrition:assessment_list', 'nutrition:diet_plan_list', 
    'nutrition:consultation_list',
    'billing:index', 'billing:invoices', 'billing:create_invoice', 'billing:payments', 'billing:services',
    'equipment:list', 'equipment:create', 'equipment:maintenance_list', 'equipment:categories',
    'accounts:users', 'accounts:create_user', 'accounts:organization', 'accounts:profile',
    'reports:index',
    'accounts:logout'
]

print(f"\n3. VERIFICACIÓN DE URLs DEL SIDEBAR:")
working_urls = []
broken_urls = []

for url_name in sidebar_urls:
    try:
        url = reverse(url_name)
        working_urls.append((url_name, url))
        print(f"   ✓ {url_name}")
    except NoReverseMatch as e:
        broken_urls.append((url_name, str(e)))
        print(f"   ✗ {url_name} - {e}")

print(f"\n   RESUMEN URLs: {len(working_urls)} funcionando, {len(broken_urls)} con errores")

# 4. Análisis de templates
template_dirs = [
    'templates/dashboard',
    'templates/patients', 
    'templates/appointments',
    'templates/medical_records',
    'templates/psychology',
    'templates/nutrition',
    'templates/billing',
    'templates/equipment',
    'templates/accounts',
    'templates/reports',
    'templates/specialties'
]

print(f"\n4. ANÁLISIS DE TEMPLATES:")
for template_dir in template_dirs:
    full_path = Path(f"C:/Users/PC FACTOR BLACK/TopicTalesBiomProyecto/{template_dir}")
    if full_path.exists():
        templates = list(full_path.glob("*.html"))
        print(f"   {template_dir}: {len(templates)} templates")
        for template in templates:
            print(f"     - {template.name}")
    else:
        print(f"   {template_dir}: DIRECTORIO NO EXISTE")

# 5. URLs faltantes que necesitan implementarse
if broken_urls:
    print(f"\n5. URLs QUE NECESITAN IMPLEMENTARSE:")
    for url_name, error in broken_urls:
        print(f"   - {url_name}: {error}")

print(f"\n=== FIN DEL ANÁLISIS ===")
print(f"Estado: {'COMPLETO' if len(broken_urls) == 0 else 'NECESITA CORRECCIONES'}")