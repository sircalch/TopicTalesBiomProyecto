#!/usr/bin/env python
"""
TopicTales Biomédica - Navigation Testing Script
Tests all sidebar navigation links to ensure they work correctly
"""
import os
import sys
import django
import requests
from urllib.parse import urljoin

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from django.core.management import execute_from_command_line

User = get_user_model()

class NavigationTester:
    def __init__(self):
        self.base_url = 'http://127.0.0.1:8001'
        self.client = Client()
        self.results = {
            'working': [],
            'broken': [],
            'requires_auth': [],
            'template_missing': []
        }
        
    def setup_test_user(self):
        """Create or get test user for authentication"""
        try:
            user = User.objects.get(username='test_nav_user')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='test_nav_user',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
        return user
    
    def test_url(self, url_name, namespace=None, args=None, kwargs=None):
        """Test a specific URL"""
        try:
            if namespace:
                full_url_name = f'{namespace}:{url_name}'
            else:
                full_url_name = url_name
                
            url = reverse(full_url_name, args=args, kwargs=kwargs)
            
            # Test without authentication first
            response = self.client.get(url)
            
            if response.status_code == 302 and 'login' in response.url:
                self.results['requires_auth'].append({
                    'url_name': full_url_name,
                    'url': url,
                    'status': 'requires_auth'
                })
                return 'requires_auth'
            elif response.status_code == 200:
                self.results['working'].append({
                    'url_name': full_url_name,
                    'url': url,
                    'status': 'working'
                })
                return 'working'
            elif response.status_code == 404:
                self.results['broken'].append({
                    'url_name': full_url_name,
                    'url': url,
                    'status': 'not_found',
                    'error': f'URL not found: {url}'
                })
                return 'not_found'
            else:
                self.results['broken'].append({
                    'url_name': full_url_name,
                    'url': url,
                    'status': f'error_{response.status_code}',
                    'error': f'HTTP {response.status_code}'
                })
                return f'error_{response.status_code}'
                
        except Exception as e:
            self.results['broken'].append({
                'url_name': full_url_name if 'full_url_name' in locals() else url_name,
                'url': url if 'url' in locals() else 'unknown',
                'status': 'exception',
                'error': str(e)
            })
            return 'exception'
    
    def test_authenticated_urls(self):
        """Test URLs that require authentication"""
        user = self.setup_test_user()
        self.client.force_login(user)
        
        auth_required_urls = []
        for item in self.results['requires_auth']:
            auth_required_urls.append(item)
        
        # Clear requires_auth for retesting
        self.results['requires_auth'] = []
        
        for item in auth_required_urls:
            try:
                url = item['url']
                response = self.client.get(url)
                
                if response.status_code == 200:
                    self.results['working'].append({
                        'url_name': item['url_name'],
                        'url': url,
                        'status': 'working_authenticated'
                    })
                elif 'TemplateDoesNotExist' in str(response.content):
                    self.results['template_missing'].append({
                        'url_name': item['url_name'],
                        'url': url,
                        'status': 'template_missing'
                    })
                else:
                    self.results['broken'].append({
                        'url_name': item['url_name'],
                        'url': url,
                        'status': f'auth_error_{response.status_code}',
                        'error': f'HTTP {response.status_code} after auth'
                    })
            except Exception as e:
                self.results['broken'].append({
                    'url_name': item['url_name'],
                    'url': url if 'url' in locals() else 'unknown',
                    'status': 'auth_exception',
                    'error': str(e)
                })
    
    def run_navigation_tests(self):
        """Run comprehensive navigation tests"""
        print("Starting Navigation Test Suite...")
        print("=" * 60)
        
        # Core navigation URLs
        navigation_urls = [
            # Dashboard
            ('dashboard', 'index'),
            
            # Patients
            ('patients', 'list'),
            ('patients', 'create'),
            ('patients', 'search'),
            
            # Appointments
            ('appointments', 'calendar'),
            ('appointments', 'list'),
            ('appointments', 'create'),
            
            # Medical Records
            ('medical_records', 'index'),
            ('medical_records', 'all_consultations'),
            ('medical_records', 'search'),
            
            # Psychology
            ('psychology', 'dashboard'),
            ('psychology', 'evaluation_list'),
            ('psychology', 'session_list'),
            ('psychology', 'treatment_plan_list'),
            ('psychology', 'test_list'),
            
            # Nutrition
            ('nutrition', 'dashboard'),
            ('nutrition', 'assessment_list'),
            ('nutrition', 'diet_plan_list'),
            ('nutrition', 'consultation_list'),
            
            # Specialties - Pediatrics
            ('specialties', 'pediatrics'),
            ('specialties', 'pediatric_consultations'),
            ('specialties', 'growth_charts'),
            ('specialties', 'vaccines'),
            ('specialties', 'development'),
            
            # Specialties - Cardiology
            ('specialties', 'cardiology'),
            ('specialties', 'ecg'),
            ('specialties', 'echo'),
            ('specialties', 'stress_test'),
            ('specialties', 'cardiac_rehabilitation'),
            
            # Specialties - Ophthalmology
            ('specialties', 'ophthalmology'),
            ('specialties', 'eye_exams'),
            ('specialties', 'vision_tests'),
            ('specialties', 'prescriptions'),
            ('specialties', 'surgeries'),
            
            # Specialties - Dentistry
            ('specialties', 'dentistry'),
            ('specialties', 'dental_exams'),
            ('specialties', 'treatments'),
            ('specialties', 'orthodontics'),
            ('specialties', 'oral_surgery'),
            
            # Specialties - Dermatology
            ('specialties', 'dermatology'),
            ('specialties', 'skin_exams'),
            ('specialties', 'dermatoscopy'),
            ('specialties', 'dermatology_treatments'),
            ('specialties', 'cosmetic'),
            
            # Specialties - Gynecology
            ('specialties', 'gynecology'),
            ('specialties', 'gynecologic_exams'),
            ('specialties', 'pregnancy'),
            ('specialties', 'pap_smear'),
            ('specialties', 'contraception'),
            
            # Specialties - Traumatology
            ('specialties', 'traumatology'),
            ('specialties', 'xrays'),
            ('specialties', 'fractures'),
            ('specialties', 'therapy'),
            ('specialties', 'orthopedic_surgeries'),
            
            # Billing
            ('billing', 'index'),
            ('billing', 'invoices'),
            ('billing', 'create_invoice'),
            ('billing', 'payments'),
            ('billing', 'services'),
            
            # Equipment
            ('equipment', 'list'),
            ('equipment', 'create'),
            ('equipment', 'maintenance_list'),
            ('equipment', 'categories'),
            
            # Accounts
            ('accounts', 'users'),
            ('accounts', 'create_user'),
            ('accounts', 'organization'),
            ('accounts', 'profile'),
            
            # Reports
            ('reports', 'index'),
        ]
        
        print(f"Testing {len(navigation_urls)} navigation URLs...")
        print()
        
        # Test each URL
        for namespace, url_name in navigation_urls:
            status = self.test_url(url_name, namespace)
            status_symbol = {
                'working': '[OK]',
                'requires_auth': '[AUTH]',
                'not_found': '[404]',
                'exception': '[ERR]'
            }.get(status, '[UNK]')
            
            print(f"{status_symbol} {namespace}:{url_name} - {status}")
        
        print()
        print("Testing authenticated URLs...")
        self.test_authenticated_urls()
        
        print()
        self.print_summary()
        
    def print_summary(self):
        """Print test results summary"""
        print("NAVIGATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = sum(len(v) for v in self.results.values())
        working_count = len(self.results['working'])
        broken_count = len(self.results['broken'])
        template_missing_count = len(self.results['template_missing'])
        
        print(f"Total URLs tested: {total_tests}")
        print(f"Working: {working_count}")
        print(f"Broken: {broken_count}")
        print(f"Template Missing: {template_missing_count}")
        
        success_rate = (working_count / total_tests * 100) if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results['broken']:
            print("\nBROKEN URLS:")
            for item in self.results['broken']:
                print(f"   * {item['url_name']}: {item['error']}")
        
        if self.results['template_missing']:
            print("\nMISSING TEMPLATES:")
            for item in self.results['template_missing']:
                print(f"   * {item['url_name']}: Template not found")
        
        print("\nWORKING URLS:")
        for item in self.results['working']:
            auth_status = " (authenticated)" if "authenticated" in item['status'] else ""
            print(f"   * {item['url_name']}{auth_status}")
        
        return {
            'total': total_tests,
            'working': working_count,
            'broken': broken_count,
            'template_missing': template_missing_count,
            'success_rate': success_rate
        }

if __name__ == '__main__':
    tester = NavigationTester()
    tester.run_navigation_tests()