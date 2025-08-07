#!/usr/bin/env python
"""
Create a test user with profile for testing navigation
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import UserProfile, Organization

User = get_user_model()

def create_test_user_with_profile():
    """Create a test user with profile and organization"""
    
    # Create or get organization
    organization, created = Organization.objects.get_or_create(
        name="Test Medical Center",
        defaults={
            'legal_name': 'Test Medical Center S.A. de C.V.',
            'tax_id': 'TMC123456789',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'address': 'Test Address 123, Test City',
            'director_name': 'Dr. Test Director',
            'director_license': '12345678'
        }
    )
    
    if created:
        print(f"Created organization: {organization.name}")
    else:
        print(f"Using existing organization: {organization.name}")
    
    # Create or get user
    user, user_created = User.objects.get_or_create(
        username='test_nav_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    
    if user_created:
        user.set_password('testpass123')
        user.save()
        print(f"Created user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")
    
    # Create or get user profile
    profile, profile_created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'organization': organization,
            'department': 'General Medicine',
            'position': 'Doctor'
        }
    )
    
    if profile_created:
        print(f"Created profile for user: {user.username}")
    else:
        print(f"Using existing profile for user: {user.username}")
    
    print("\nTest user setup complete!")
    print(f"Username: {user.username}")
    print(f"Password: testpass123")
    print(f"Organization: {organization.name}")
    print(f"Position: {profile.position}")
    
    return user, profile, organization

if __name__ == '__main__':
    create_test_user_with_profile()