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
from django.urls import reverse

print("=== Prueba de Funcionalidad Básica ===")

# Create test client
client = Client()

# Test login
print("\n1. Probando login...")
user = User.objects.filter(username='admin').first()
if user:
    login_response = client.login(username='admin', password='admin123')
    print(f"Login exitoso: {login_response}")
    
    # Test dashboard access
    print("\n2. Probando acceso al dashboard...")
    try:
        dashboard_response = client.get('/dashboard/')
        print(f"Dashboard status: {dashboard_response.status_code}")
        if dashboard_response.status_code == 200:
            print("✓ Dashboard carga correctamente")
        else:
            print(f"✗ Dashboard error: {dashboard_response.status_code}")
            print(f"Content: {dashboard_response.content[:500]}")
    except Exception as e:
        print(f"✗ Error en dashboard: {e}")
    
    # Test patients list
    print("\n3. Probando lista de pacientes...")
    try:
        patients_response = client.get('/patients/')
        print(f"Patients status: {patients_response.status_code}")
        if patients_response.status_code == 200:
            print("✓ Lista de pacientes carga correctamente")
        else:
            print(f"✗ Pacientes error: {patients_response.status_code}")
    except Exception as e:
        print(f"✗ Error en pacientes: {e}")
    
    # Test appointments
    print("\n4. Probando sistema de citas...")
    try:
        appointments_response = client.get('/appointments/')
        print(f"Appointments status: {appointments_response.status_code}")
        if appointments_response.status_code == 200:
            print("✓ Sistema de citas carga correctamente")
        else:
            print(f"✗ Citas error: {appointments_response.status_code}")
    except Exception as e:
        print(f"✗ Error en citas: {e}")
    
    # Test medical records
    print("\n5. Probando expedientes médicos...")
    try:
        records_response = client.get('/medical-records/')
        print(f"Medical records status: {records_response.status_code}")
        if records_response.status_code == 200:
            print("✓ Expedientes médicos carga correctamente")
        else:
            print(f"✗ Expedientes error: {records_response.status_code}")
    except Exception as e:
        print(f"✗ Error en expedientes: {e}")
    
    # Test psychology module
    print("\n6. Probando módulo de psicología...")
    try:
        psychology_response = client.get('/psychology/')
        print(f"Psychology status: {psychology_response.status_code}")
        if psychology_response.status_code == 200:
            print("✓ Módulo de psicología carga correctamente")
        else:
            print(f"✗ Psicología error: {psychology_response.status_code}")
    except Exception as e:
        print(f"✗ Error en psicología: {e}")
    
    # Test nutrition module
    print("\n7. Probando módulo de nutrición...")
    try:
        nutrition_response = client.get('/nutrition/')
        print(f"Nutrition status: {nutrition_response.status_code}")
        if nutrition_response.status_code == 200:
            print("✓ Módulo de nutrición carga correctamente")
        else:
            print(f"✗ Nutrición error: {nutrition_response.status_code}")
    except Exception as e:
        print(f"✗ Error en nutrición: {e}")

else:
    print("✗ Usuario admin no encontrado")

print("\n=== Prueba de Funcionalidad Completada ===")