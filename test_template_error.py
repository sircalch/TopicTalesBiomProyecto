#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.template import Template, Context
from django.template.loader import get_template
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from accounts.models import User, UserProfile, Organization, Subscription

print("=== Test Template Error ===")

try:
    # Get a user
    user = User.objects.first()
    print(f"Testing with user: {user.username}")
    
    # Test accessing profile
    profile = user.profile
    print(f"User profile: {profile}")
    
    # Test accessing organization
    organization = profile.organization
    print(f"Organization: {organization}")
    
    # Test accessing subscription
    subscription = organization.subscription
    print(f"Subscription: {subscription}")
    
    # Test the has_feature method
    print(f"Subscription plan: {subscription.plan}")
    print(f"Testing has_feature method...")
    
    # Test specific features
    features_to_test = [
        'medical_history',
        'patient_management', 
        'advanced_appointments',
        'all_specialty_modules',
        'equipment_management',
        'billing_module'
    ]
    
    for feature in features_to_test:
        try:
            result = subscription.has_feature(feature)
            print(f"  - {feature}: {result}")
        except Exception as e:
            print(f"  - {feature}: ERROR - {e}")
    
    # Test template rendering with context
    print("\n=== Testing Template Context ===")
    factory = RequestFactory()
    request = factory.get('/dashboard/')
    request.user = user
    
    # Test context processors
    from accounts.context_processors import sidebar_modules, subscription_features
    
    sidebar_context = sidebar_modules(request)
    print(f"Sidebar context: {list(sidebar_context.keys())}")
    
    features_context = subscription_features(request)
    print(f"Features context: {list(features_context.keys())}")
    
    print("\n=== Test Template Rendering ===")
    template_str = """
    {% load static %}
    User: {{ user.username }}
    Plan: {{ user.profile.organization.subscription.plan }}
    Has medical history: {{ user.profile.organization.subscription.has_medical_history }}
    """
    
    template = Template(template_str)
    context = Context({
        'user': user,
        'request': request
    })
    
    rendered = template.render(context)
    print("Template rendered successfully:")
    print(rendered)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()