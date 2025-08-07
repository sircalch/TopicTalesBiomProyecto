#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate

print("=== Verificacion de Usuarios ===")

# List all users
users = User.objects.all()
print(f"\nUsuarios en la base de datos ({users.count()}):")
for user in users:
    print(f"- Usuario: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Rol: {user.get_role_display()}")
    print(f"  Activo: {user.is_active}")
    print(f"  Staff: {user.is_staff}")
    print(f"  Superuser: {user.is_superuser}")
    print(f"  Fecha creacion: {user.date_joined}")
    print()

# Test authentication with common passwords
test_passwords = ['admin123', 'admin', 'password', 'doctor123', 'recep123']
test_users = ['admin', 'dr.martinez', 'recepcion', 'doctor', 'superadmin']

print("=== Prueba de Autenticacion ===")
working_credentials = []

for username in test_users:
    if User.objects.filter(username=username).exists():
        print(f"\nProbando usuario: {username}")
        for password in test_passwords:
            user = authenticate(username=username, password=password)
            if user:
                print(f"  ✓ {username} / {password} - FUNCIONA")
                working_credentials.append((username, password))
            else:
                print(f"  ✗ {username} / {password} - No funciona")

print(f"\n=== Credenciales que funcionan ===")
if working_credentials:
    for username, password in working_credentials:
        user = User.objects.get(username=username)
        print(f"Usuario: {username}")
        print(f"Contraseña: {password}")
        print(f"Rol: {user.get_role_display()}")
        print(f"Organización: {user.profile.organization.name if hasattr(user, 'profile') else 'Sin perfil'}")
        print("---")
else:
    print("¡No se encontraron credenciales válidas!")
    print("\nCreando usuario de prueba...")
    
    # Create test user
    try:
        test_user = User.objects.create_user(
            username='test_admin',
            email='admin@test.com',
            password='test123',
            role='admin',
            first_name='Admin',
            last_name='Test'
        )
        print(f"Usuario creado: test_admin / test123")
    except Exception as e:
        print(f"Error creando usuario: {e}")
        
print(f"\n=== Para acceder al sistema ===")
if working_credentials:
    username, password = working_credentials[0]
    print(f"URL: http://127.0.0.1:8000")
    print(f"Usuario: {username}")
    print(f"Contraseña: {password}")
else:
    print("URL: http://127.0.0.1:8000")
    print("Usuario: test_admin")
    print("Contraseña: test123")