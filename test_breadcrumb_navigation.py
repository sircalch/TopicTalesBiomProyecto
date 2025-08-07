#!/usr/bin/env python
"""
TopicTales Biomédica - Breadcrumb Navigation Testing
Tests breadcrumb functionality and navigation consistency
"""
import os
import sys
import django
from bs4 import BeautifulSoup

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

class BreadcrumbTester:
    def __init__(self):
        self.client = Client()
        self.results = {
            'breadcrumb_tests': [],
            'navigation_consistency': [],
            'working_links': 0,
            'broken_links': 0
        }
        
    def setup_authenticated_client(self):
        """Setup authenticated client"""
        try:
            user = User.objects.get(username='test_nav_user')
            self.client.force_login(user)
            return True
        except User.DoesNotExist:
            print("Error: Test user not found.")
            return False
    
    def test_breadcrumb_navigation(self, url_path, page_name):
        """Test breadcrumb navigation on a specific page"""
        try:
            response = self.client.get(url_path)
            
            if response.status_code != 200:
                return {'page': page_name, 'status': 'error', 'issue': f'HTTP {response.status_code}'}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find breadcrumb
            breadcrumb_nav = soup.find('nav', {'aria-label': 'breadcrumb'})
            if not breadcrumb_nav:
                breadcrumb_nav = soup.find('ol', class_='breadcrumb')
            
            if not breadcrumb_nav:
                return {'page': page_name, 'status': 'no_breadcrumb', 'url': url_path}
            
            # Extract breadcrumb items
            breadcrumb_items = breadcrumb_nav.find_all('li', class_='breadcrumb-item')
            
            breadcrumb_data = []
            working_links = 0
            broken_links = 0
            
            for item in breadcrumb_items:
                link = item.find('a')
                if link and 'href' in link.attrs:
                    href = link.attrs['href']
                    text = link.get_text(strip=True)
                    
                    # Test if link works
                    if href.startswith('/') and not href.startswith('javascript:'):
                        try:
                            link_response = self.client.get(href)
                            link_status = 'working' if link_response.status_code == 200 else f'error_{link_response.status_code}'
                            if link_response.status_code == 200:
                                working_links += 1
                            else:
                                broken_links += 1
                        except:
                            link_status = 'exception'
                            broken_links += 1
                    else:
                        link_status = 'external_or_js'
                    
                    breadcrumb_data.append({
                        'text': text,
                        'href': href,
                        'status': link_status
                    })
                else:
                    # Active breadcrumb (no link)
                    text = item.get_text(strip=True)
                    breadcrumb_data.append({
                        'text': text,
                        'href': None,
                        'status': 'active'
                    })
            
            self.results['working_links'] += working_links
            self.results['broken_links'] += broken_links
            
            return {
                'page': page_name,
                'url': url_path,
                'status': 'success',
                'breadcrumb_count': len(breadcrumb_data),
                'breadcrumbs': breadcrumb_data,
                'working_links': working_links,
                'broken_links': broken_links
            }
            
        except Exception as e:
            return {'page': page_name, 'status': 'exception', 'error': str(e)}
    
    def run_breadcrumb_tests(self):
        """Run comprehensive breadcrumb tests"""
        print("Starting Breadcrumb Navigation Test Suite...")
        print("=" * 60)
        
        if not self.setup_authenticated_client():
            return
        
        # Test pages with different breadcrumb depths
        test_pages = [
            # Level 1: Main sections
            ('/dashboard/', 'Dashboard'),
            ('/patients/', 'Patients'),
            ('/appointments/', 'Appointments'),
            
            # Level 2: Specialty main pages
            ('/specialties/pediatrics/', 'Pediatrics Main'),
            ('/specialties/cardiology/', 'Cardiology Main'),
            ('/specialties/dermatology/', 'Dermatology Main'),
            ('/psychology/', 'Psychology Main'),
            ('/nutrition/', 'Nutrition Main'),
            
            # Level 3: Specialty sub-pages
            ('/specialties/pediatrics/consultations/', 'Pediatric Consultations'),
            ('/specialties/cardiology/ecg/', 'ECG'),
            ('/specialties/dermatology/dermatoscopy/', 'Dermatoscopy'),
            ('/specialties/gynecology/pregnancy/', 'Pregnancy Control'),
            ('/specialties/traumatology/fractures/', 'Fractures'),
            
            # Other sections
            ('/billing/', 'Billing'),
            ('/equipment/', 'Equipment'),
            ('/reports/', 'Reports'),
            ('/accounts/users/', 'User Management')
        ]
        
        print(f"Testing breadcrumb navigation on {len(test_pages)} pages...")
        print()
        
        for url_path, page_name in test_pages:
            result = self.test_breadcrumb_navigation(url_path, page_name)
            self.results['breadcrumb_tests'].append(result)
            
            status_symbol = {
                'success': '[OK]',
                'no_breadcrumb': '[NO-BC]',
                'error': '[ERR]',
                'exception': '[EXC]'
            }.get(result['status'], '[UNK]')
            
            if result['status'] == 'success':
                breadcrumb_info = f" ({result['breadcrumb_count']} items, {result['working_links']} working links)"
                print(f"{status_symbol} {page_name}{breadcrumb_info}")
            else:
                print(f"{status_symbol} {page_name} - {result.get('issue', result.get('error', 'Unknown issue'))}")
        
        print()
        self.print_breadcrumb_summary()
    
    def print_breadcrumb_summary(self):
        """Print breadcrumb test summary"""
        print("BREADCRUMB NAVIGATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results['breadcrumb_tests'])
        successful_tests = len([t for t in self.results['breadcrumb_tests'] if t['status'] == 'success'])
        
        print(f"Total Pages Tested: {total_tests}")
        print(f"Pages with Working Breadcrumbs: {successful_tests}")
        print(f"Breadcrumb Success Rate: {(successful_tests/total_tests*100):.1f}%")
        print(f"Total Breadcrumb Links Working: {self.results['working_links']}")
        print(f"Total Breadcrumb Links Broken: {self.results['broken_links']}")
        
        if self.results['working_links'] > 0:
            link_success_rate = self.results['working_links'] / (self.results['working_links'] + self.results['broken_links']) * 100
            print(f"Breadcrumb Link Success Rate: {link_success_rate:.1f}%")
        
        # Show detailed breadcrumb structure for some pages
        print("\nSAMPLE BREADCRUMB STRUCTURES:")
        sample_pages = [t for t in self.results['breadcrumb_tests'] if t['status'] == 'success'][:5]
        
        for page in sample_pages:
            print(f"\n{page['page']} ({page['url']}):")
            breadcrumb_path = " > ".join([
                f"{bc['text']}" + ("*" if bc['status'] == 'active' else "") 
                for bc in page['breadcrumbs']
            ])
            print(f"   {breadcrumb_path}")
        
        # Show issues if any
        issues = [t for t in self.results['breadcrumb_tests'] if t['status'] != 'success']
        if issues:
            print("\nISSUES FOUND:")
            for issue in issues:
                print(f"   • {issue['page']}: {issue.get('issue', issue.get('error', 'Unknown'))}")
        else:
            print("\nAll breadcrumb navigation is working perfectly!")

if __name__ == '__main__':
    tester = BreadcrumbTester()
    tester.run_breadcrumb_tests()