#!/usr/bin/env python
"""
TopicTales Biomédica - Template Functionality Testing
Tests template rendering, button functionality, and visual elements
"""
import os
import sys
import django
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

class TemplateFunctionalityTester:
    def __init__(self):
        self.base_url = 'http://127.0.0.1:8001'
        self.client = Client()
        self.results = {
            'tested_pages': [],
            'working_elements': [],
            'issues_found': [],
            'template_quality': []
        }
        
    def setup_authenticated_client(self):
        """Setup authenticated client for testing"""
        try:
            user = User.objects.get(username='test_nav_user')
            self.client.force_login(user)
            return True
        except User.DoesNotExist:
            print("Error: Test user not found. Run create_test_user.py first.")
            return False
    
    def test_page_content(self, url_path, page_name):
        """Test specific page for content quality and functionality"""
        try:
            response = self.client.get(url_path)
            
            if response.status_code != 200:
                self.results['issues_found'].append({
                    'page': page_name,
                    'issue': f'HTTP {response.status_code}',
                    'url': url_path
                })
                return False
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Test elements
            page_result = {
                'page_name': page_name,
                'url': url_path,
                'title': soup.find('title').text if soup.find('title') else 'No title',
                'has_breadcrumb': bool(soup.find('nav', {'aria-label': 'breadcrumb'})),
                'button_count': len(soup.find_all('button')),
                'link_count': len(soup.find_all('a')),
                'card_count': len(soup.find_all('div', class_='card')),
                'table_count': len(soup.find_all('table')),
                'form_count': len(soup.find_all('form')),
                'has_sidebar': bool(soup.find('div', {'id': 'sidebar'})),
                'has_navbar': bool(soup.find('nav', class_='navbar')),
                'responsive_classes': self._check_responsive_classes(soup),
                'bootstrap_components': self._check_bootstrap_components(soup)
            }
            
            self.results['tested_pages'].append(page_result)
            
            # Quality checks
            quality_score = self._calculate_quality_score(page_result, soup)
            self.results['template_quality'].append({
                'page': page_name,
                'score': quality_score,
                'details': self._get_quality_details(soup)
            })
            
            return True
            
        except Exception as e:
            self.results['issues_found'].append({
                'page': page_name,
                'issue': f'Exception: {str(e)}',
                'url': url_path
            })
            return False
    
    def _check_responsive_classes(self, soup):
        """Check for responsive Bootstrap classes"""
        responsive_indicators = [
            'col-', 'row', 'container', 'container-fluid',
            'd-none', 'd-block', 'd-sm-', 'd-md-', 'd-lg-', 'd-xl-'
        ]
        
        found_classes = []
        for indicator in responsive_indicators:
            if soup.find(attrs={'class': lambda x: x and indicator in ' '.join(x.split())}):
                found_classes.append(indicator)
        
        return found_classes
    
    def _check_bootstrap_components(self, soup):
        """Check for Bootstrap components"""
        components = {
            'cards': len(soup.find_all('div', class_='card')),
            'buttons': len(soup.find_all('button', class_='btn')),
            'badges': len(soup.find_all(attrs={'class': lambda x: x and 'badge' in ' '.join(x.split()) if x else False})),
            'alerts': len(soup.find_all(attrs={'class': lambda x: x and 'alert' in ' '.join(x.split()) if x else False})),
            'modals': len(soup.find_all(attrs={'class': lambda x: x and 'modal' in ' '.join(x.split()) if x else False})),
            'forms': len(soup.find_all('form')),
            'tables': len(soup.find_all('table', class_='table'))
        }
        
        return components
    
    def _calculate_quality_score(self, page_result, soup):
        """Calculate page quality score (0-100)"""
        score = 0
        
        # Basic structure (30 points)
        if page_result['has_breadcrumb']: score += 5
        if page_result['has_sidebar']: score += 5
        if page_result['has_navbar']: score += 5
        if soup.find('title'): score += 5
        if soup.find('h1') or soup.find('h2'): score += 10
        
        # Interactive elements (20 points)
        if page_result['button_count'] > 0: score += 10
        if page_result['link_count'] > 5: score += 10
        
        # Content richness (25 points)
        if page_result['card_count'] > 0: score += 10
        if page_result['table_count'] > 0: score += 5
        if page_result['form_count'] > 0: score += 10
        
        # Design quality (25 points)
        if len(page_result['responsive_classes']) > 5: score += 10
        if soup.find('i', class_='fas'): score += 5  # FontAwesome icons
        if soup.find(attrs={'class': lambda x: x and any(color in ' '.join(x.split()) for color in ['text-primary', 'text-success', 'text-warning', 'text-danger']) if x else False}): score += 5
        if soup.find('div', class_='shadow'): score += 5  # Shadow effects
        
        return min(score, 100)
    
    def _get_quality_details(self, soup):
        """Get detailed quality information"""
        details = {
            'has_medical_content': bool(soup.find(string=lambda text: any(word in text.lower() if text else False for word in ['paciente', 'consulta', 'médico', 'tratamiento', 'diagnóstico']))),
            'has_data_tables': bool(soup.find('table')),
            'has_action_buttons': bool(soup.find('button', class_='btn')),
            'has_forms': bool(soup.find('form')),
            'has_icons': bool(soup.find('i', class_='fas')),
            'has_professional_styling': bool(soup.find(attrs={'class': lambda x: x and any(style in ' '.join(x.split()) for style in ['shadow', 'rounded', 'gradient']) if x else False}))
        }
        return details
    
    def run_comprehensive_test(self):
        """Run comprehensive template functionality tests"""
        print("Starting Template Functionality Test Suite...")
        print("=" * 60)
        
        if not self.setup_authenticated_client():
            return
        
        # Test key pages
        test_pages = [
            ('/dashboard/', 'Dashboard Principal'),
            ('/patients/', 'Lista de Pacientes'),
            ('/appointments/', 'Calendario de Citas'),
            ('/specialties/pediatrics/', 'Pediatría Dashboard'),
            ('/specialties/pediatrics/consultations/', 'Consultas Pediátricas'),
            ('/specialties/cardiology/', 'Cardiología Dashboard'),
            ('/specialties/cardiology/ecg/', 'Electrocardiogramas'),
            ('/specialties/ophthalmology/', 'Oftalmología Dashboard'),
            ('/specialties/dentistry/', 'Odontología Dashboard'),
            ('/specialties/dermatology/', 'Dermatología Dashboard'),
            ('/specialties/dermatology/dermatoscopy/', 'Dermatoscopia'),
            ('/specialties/gynecology/', 'Ginecología Dashboard'),
            ('/specialties/gynecology/pregnancy/', 'Control Prenatal'),
            ('/specialties/traumatology/', 'Traumatología Dashboard'),
            ('/psychology/', 'Psicología Dashboard'),
            ('/nutrition/', 'Nutrición Dashboard'),
            ('/billing/', 'Facturación Dashboard'),
            ('/equipment/', 'Lista de Equipos'),
            ('/reports/', 'Reportes Dashboard'),
            ('/accounts/users/', 'Gestión de Usuarios')
        ]
        
        print(f"Testing {len(test_pages)} key pages for functionality and quality...")
        print()
        
        success_count = 0
        for url_path, page_name in test_pages:
            success = self.test_page_content(url_path, page_name)
            status = "[OK]" if success else "[ERROR]"
            print(f"{status} {page_name}")
            if success:
                success_count += 1
        
        print()
        self.print_results()
        
        return {
            'total_tested': len(test_pages),
            'successful': success_count,
            'success_rate': (success_count / len(test_pages) * 100) if test_pages else 0
        }
    
    def print_results(self):
        """Print comprehensive test results"""
        print("TEMPLATE FUNCTIONALITY TEST RESULTS")
        print("=" * 60)
        
        if self.results['tested_pages']:
            avg_quality = sum(q['score'] for q in self.results['template_quality']) / len(self.results['template_quality'])
            print(f"Average Template Quality Score: {avg_quality:.1f}/100")
            print()
            
            print("TOP QUALITY PAGES:")
            sorted_quality = sorted(self.results['template_quality'], key=lambda x: x['score'], reverse=True)
            for i, page in enumerate(sorted_quality[:5], 1):
                print(f"   {i}. {page['page']} - {page['score']}/100")
            
            print("\nTEMPLATE FEATURES SUMMARY:")
            total_buttons = sum(p['button_count'] for p in self.results['tested_pages'])
            total_cards = sum(p['card_count'] for p in self.results['tested_pages'])
            total_tables = sum(p['table_count'] for p in self.results['tested_pages'])
            total_forms = sum(p['form_count'] for p in self.results['tested_pages'])
            
            print(f"   • Total Interactive Buttons: {total_buttons}")
            print(f"   • Total Bootstrap Cards: {total_cards}")
            print(f"   • Total Data Tables: {total_tables}")
            print(f"   • Total Forms: {total_forms}")
            
            pages_with_breadcrumbs = sum(1 for p in self.results['tested_pages'] if p['has_breadcrumb'])
            print(f"   • Pages with Breadcrumbs: {pages_with_breadcrumbs}/{len(self.results['tested_pages'])}")
        
        if self.results['issues_found']:
            print("\nISSUES FOUND:")
            for issue in self.results['issues_found']:
                print(f"   • {issue['page']}: {issue['issue']}")
        else:
            print("\nNo issues found - All templates are working correctly!")

if __name__ == '__main__':
    tester = TemplateFunctionalityTester()
    results = tester.run_comprehensive_test()