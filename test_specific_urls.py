#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import User

print("=== Prueba de URLs Específicas ===")

# Create test client
client = Client()

# Login as admin
user = User.objects.filter(username='admin').first()
if user:
    login_success = client.login(username='admin', password='admin123')
    print(f"Login exitoso: {login_success}")
    
    if login_success:
        # Test specific problematic URLs
        test_urls = [
            ('/billing/', 'Facturación'),
            ('/equipment/', 'Equipos'),
            ('/reports/', 'Reportes'),
            ('/equipment/categories/', 'Categorías de Equipos'),
            ('/equipment/maintenance/', 'Mantenimientos'),
            ('/billing/invoices/', 'Facturas'),
            ('/billing/services/', 'Servicios'),
            ('/billing/payments/', 'Pagos'),
        ]
        
        working_urls = []
        broken_urls = []
        
        for url, name in test_urls:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    working_urls.append((url, name))
                    print(f"[OK] {name} ({url}) - Status: {response.status_code}")
                else:
                    broken_urls.append((url, name, response.status_code))
                    print(f"[ERROR] {name} ({url}) - Status: {response.status_code}")
                    if response.status_code == 500:
                        print(f"  Error 500 en: {name}")
            except Exception as e:
                broken_urls.append((url, name, str(e)))
                print(f"[EXCEPTION] {name} ({url}) - Error: {e}")
        
        print(f"\n=== Resumen ===")
        print(f"URLs funcionando: {len(working_urls)}")
        print(f"URLs con problemas: {len(broken_urls)}")
        
        if working_urls:
            print(f"\nURLs que funcionan:")
            for url, name in working_urls:
                print(f"  - {name}: {url}")
        
        if broken_urls:
            print(f"\nURLs con problemas:")
            for url, name, error in broken_urls:
                print(f"  - {name}: {url} -> {error}")
    else:
        print("No se pudo hacer login")
else:
    print("Usuario admin no encontrado")