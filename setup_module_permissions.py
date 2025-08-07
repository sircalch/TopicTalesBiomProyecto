#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from accounts.models import Organization, SystemModule, ModulePermission

print("=== Configurando Permisos de Módulos ===")

organizations = Organization.objects.all()
modules = SystemModule.objects.all()

for org in organizations:
    print(f"\nConfigurando organización: {org.name}")
    subscription = getattr(org, 'subscription', None)
    
    if not subscription:
        print(f"  ⚠️  {org.name} no tiene suscripción")
        continue
    
    print(f"  Plan: {subscription.get_plan_display()}")
    
    for module in modules:
        # Check if module is available for this plan
        if module.is_available_for_plan(subscription.plan):
            # Create or update module permission
            permission, created = ModulePermission.objects.get_or_create(
                organization=org,
                module=module,
                defaults={'is_enabled': True}
            )
            
            if created:
                print(f"  [+] Creado permiso: {module.display_name}")
            else:
                if not permission.is_enabled:
                    permission.is_enabled = True
                    permission.save()
                    print(f"  [*] Habilitado: {module.display_name}")
                else:
                    print(f"  [OK] Ya configurado: {module.display_name}")
        else:
            # Check if permission exists and disable it
            try:
                permission = ModulePermission.objects.get(
                    organization=org,
                    module=module
                )
                if permission.is_enabled:
                    permission.is_enabled = False
                    permission.save()
                    print(f"  [-] Deshabilitado: {module.display_name} (no disponible en {subscription.plan})")
            except ModulePermission.DoesNotExist:
                print(f"  [SKIP] {module.display_name} no disponible en {subscription.plan}")

print(f"\n=== Resumen de Configuracion ===")
for org in organizations:
    print(f"\n{org.name}:")
    permissions = ModulePermission.objects.filter(organization=org, is_enabled=True)
    for perm in permissions:
        print(f"  [OK] {perm.module.display_name}")

print("\nConfiguracion de permisos completada!")