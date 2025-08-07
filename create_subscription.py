#!/usr/bin/env python
"""
Create subscription for test organization
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from accounts.models import Organization, Subscription

def create_test_subscription():
    """Create subscription for test organization"""
    
    try:
        organization = Organization.objects.get(name="Test Medical Center")
        
        # Create or get subscription
        subscription, created = Subscription.objects.get_or_create(
            organization=organization,
            defaults={
                'plan': 'ADVANCED',
                'status': 'active',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=365),
                'max_patients': -1,  # Unlimited
                'max_users': -1,     # Unlimited
                'monthly_price': 299.99
            }
        )
        
        if created:
            print(f"Created subscription for: {organization.name}")
        else:
            print(f"Using existing subscription for: {organization.name}")
        
        print(f"Plan: {subscription.get_plan_display()}")
        print(f"Status: {subscription.get_status_display()}")
        print(f"Max Patients: {'Unlimited' if subscription.max_patients == -1 else subscription.max_patients}")
        print(f"Max Users: {'Unlimited' if subscription.max_users == -1 else subscription.max_users}")
        
        return subscription
        
    except Organization.DoesNotExist:
        print("Error: Test Medical Center organization not found. Run create_test_user.py first.")
        return None

if __name__ == '__main__':
    create_test_subscription()