#!/usr/bin/env python
"""
Test script to verify all medical application functionality
Tests all navbar and sidebar links after authentication
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

User = get_user_model()

def test_medical_functionality():
    """Test all medical application functionality after login"""
    
    # Create test client
    client = Client()
    
    # Get test user
    try:
        user = User.objects.get(username='admin')
        print(f"Testing with user: {user.username}")
    except User.DoesNotExist:
        print("No admin user found. Creating one...")
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    # Login
    login_success = client.login(username=user.username, password='admin123' if user.username == 'admin' else 'testpass123')
    if not login_success:
        # Try different password
        login_success = client.login(username=user.username, password='password')
    
    if not login_success:
        print("[FAIL] Login failed - cannot test authenticated functionality")
        return
    
    print("[OK] Login successful")
    
    # URLs to test from navbar and sidebar
    test_urls = {
        'Dashboard': '/dashboard/',
        'Patient List': '/patients/',
        'Create Patient': '/patients/create/',
        'Patient Search': '/patients/search/',
        'Appointments Calendar': '/appointments/',
        'Appointments List': '/appointments/list/',
        'Create Appointment': '/appointments/create/',
        'Medical Records': '/medical-records/',
        'Reports': '/reports/',
        'User Profile': '/accounts/profile/',
        'User Settings': '/accounts/settings/',
        'Nutrition Dashboard': '/nutrition/',
        'Psychology Dashboard': '/psychology/',
        'Equipment': '/equipment/',
        'Billing': '/billing/',
    }
    
    results = {}
    
    for name, url in test_urls.items():
        try:
            response = client.get(url)
            status = response.status_code
            
            if status == 200:
                # Check if it's a proper page or just a redirect
                content = response.content.decode('utf-8', errors='ignore')
                if 'TopicTales Biomédica' in content or 'pcoded-header' in content:
                    results[name] = {'status': 'SUCCESS', 'code': status, 'message': 'Page loads correctly'}
                else:
                    results[name] = {'status': 'WARNING', 'code': status, 'message': 'Page loads but may be incomplete'}
            elif status == 302:
                results[name] = {'status': 'REDIRECT', 'code': status, 'message': f'Redirects to: {response.url}'}
            elif status == 404:
                results[name] = {'status': 'NOT_FOUND', 'code': status, 'message': 'Page not found'}
            elif status == 500:
                results[name] = {'status': 'ERROR', 'code': status, 'message': 'Server error'}
            else:
                results[name] = {'status': 'UNKNOWN', 'code': status, 'message': f'Status: {status}'}
                
        except Exception as e:
            results[name] = {'status': 'EXCEPTION', 'code': 'N/A', 'message': str(e)}
    
    # Print results
    print("\n" + "="*80)
    print("MEDICAL APPLICATION FUNCTIONALITY TEST RESULTS")
    print("="*80)
    
    success_count = 0
    total_count = len(results)
    
    for name, result in results.items():
        status_emoji = {
            'SUCCESS': '[OK]',
            'WARNING': '[WARN]',
            'REDIRECT': '[REDIR]',
            'NOT_FOUND': '[404]',
            'ERROR': '[ERROR]',
            'EXCEPTION': '[EXCEPT]',
            'UNKNOWN': '[?]'
        }.get(result['status'], '[?]')
        
        print(f"{status_emoji} {name:<25} | Status: {result['code']:<3} | {result['message']}")
        
        if result['status'] == 'SUCCESS':
            success_count += 1
    
    print("\n" + "="*80)
    print(f"SUMMARY: {success_count}/{total_count} pages working correctly ({success_count/total_count*100:.1f}%)")
    print("="*80)
    
    # Test specific form functionality
    print("\nTesting specific form functionality...")
    
    # Test patient creation form
    try:
        response = client.get('/patients/create/')
        if response.status_code == 200:
            content = response.content.decode('utf-8', errors='ignore')
            if 'form' in content.lower() or 'input' in content.lower():
                print("[OK] Patient creation form appears to be functional")
            else:
                print("[WARN] Patient creation page loads but form may be missing")
        else:
            print(f"[FAIL] Patient creation form not accessible (status: {response.status_code})")
    except Exception as e:
        print(f"[ERROR] Error testing patient form: {e}")
    
    # Test appointment creation form
    try:
        response = client.get('/appointments/create/')
        if response.status_code == 200:
            content = response.content.decode('utf-8', errors='ignore')
            if 'form' in content.lower() or 'input' in content.lower():
                print("[OK] Appointment creation form appears to be functional")
            else:
                print("[WARN] Appointment creation page loads but form may be missing")
        else:
            print(f"[FAIL] Appointment creation form not accessible (status: {response.status_code})")
    except Exception as e:
        print(f"[ERROR] Error testing appointment form: {e}")

if __name__ == '__main__':
    test_medical_functionality()