#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from accounts.models import User, UserProfile, Organization, Subscription

print("=== Verificación de Usuarios y Perfiles ===")

# Check users without profiles
users_without_profile = User.objects.filter(profile__isnull=True)
print(f"Usuarios sin perfil: {users_without_profile.count()}")
for user in users_without_profile:
    print(f"  - {user.username} ({user.email})")

# Check users with profiles but no organization
users_without_org = User.objects.filter(profile__organization__isnull=True)
print(f"\nUsuarios sin organización: {users_without_org.count()}")
for user in users_without_org:
    print(f"  - {user.username}")

# Check organizations without subscriptions
orgs_without_sub = Organization.objects.filter(subscription__isnull=True)
print(f"\nOrganizaciones sin suscripción: {orgs_without_sub.count()}")
for org in orgs_without_sub:
    print(f"  - {org.name}")

# Print all organizations and their subscriptions
print(f"\n=== Organizaciones existentes ===")
for org in Organization.objects.all():
    sub = getattr(org, 'subscription', None)
    print(f"- {org.name}: {sub.get_plan_display() if sub else 'Sin suscripción'}")

print(f"\n=== Usuarios existentes ===")
for user in User.objects.all():
    profile = getattr(user, 'profile', None)
    org = profile.organization if profile else None
    print(f"- {user.username} ({user.get_role_display()}): {org.name if org else 'Sin organización'}")