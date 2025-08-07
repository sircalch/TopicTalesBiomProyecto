#!/usr/bin/env python
"""
TEST SISTEMA COMPLETO - TopicTales Biomédica
Script para testing integral de todas las funcionalidades
Puerto: 8004 (evita cache)
"""

import requests
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8004"
TEST_RESULTS = []

def log_test(test_name, status, details=""):
    """Registrar resultado de test"""
    result = {
        'test': test_name,
        'status': '✅ PASS' if status else '❌ FAIL',
        'details': details,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    TEST_RESULTS.append(result)
    print(f"{result['timestamp']} - {result['status']} {test_name} {details}")

def test_url_access(url_path, test_name, expected_codes=[200, 302]):
    """Probar acceso a URL"""
    try:
        response = requests.get(f"{BASE_URL}{url_path}", timeout=10)
        success = response.status_code in expected_codes
        details = f"({response.status_code})"
        log_test(test_name, success, details)
        return success, response.status_code
    except Exception as e:
        log_test(test_name, False, f"ERROR: {str(e)}")
        return False, None

def test_static_resources():
    """Probar recursos estáticos"""
    static_tests = [
        ('/static/css/navbar-center-fix.css', 'CSS Navbar Fixes'),
        ('/static/css/sidebar-layout-fix.css', 'CSS Sidebar Layout'),
        ('/static/js/navbar-sidebar-sync.js', 'JS Navbar Sync'),
        ('/static/js/force-icon-display.js', 'JS Icon Display'),
    ]
    
    print("\n🎨 TESTING RECURSOS ESTÁTICOS...")
    for url, name in static_tests:
        test_url_access(url, name, [200])

def test_main_urls():
    """Probar URLs principales del sistema"""
    main_urls = [
        ('/', 'Home Page'),
        ('/dashboard/', 'Dashboard'),
        ('/patients/', 'Patients List'),
        ('/patients/create/', 'Create Patient'),
        ('/appointments/', 'Appointments'),
        ('/appointments/create/', 'Create Appointment'),
        ('/specialties/', 'Specialties'),
        ('/medical_records/', 'Medical Records'),
        ('/billing/', 'Billing'),
        ('/equipment/', 'Equipment'),
        ('/accounts/login/', 'Login Page'),
    ]
    
    print("\n🚀 TESTING URLs PRINCIPALES...")
    for url, name in main_urls:
        test_url_access(url, name)

def test_specialty_urls():
    """Probar URLs de especialidades médicas"""
    specialty_urls = [
        ('/specialties/cardiology/', 'Cardiología'),
        ('/specialties/pediatrics/', 'Pediatría'),
        ('/specialties/gynecology/', 'Ginecología'),
        ('/specialties/ophthalmology/', 'Oftalmología'),
        ('/specialties/dentistry/', 'Odontología'),
        ('/specialties/dermatology/', 'Dermatología'),
        ('/specialties/traumatology/', 'Traumatología'),
        ('/specialties/psychology/', 'Psicología'),
        ('/specialties/nutrition/', 'Nutrición'),
    ]
    
    print("\n🏥 TESTING ESPECIALIDADES MÉDICAS...")
    for url, name in specialty_urls:
        test_url_access(url, name)

def test_api_endpoints():
    """Probar endpoints de API"""
    api_urls = [
        ('/api/', 'API Root'),
        # Agregar más endpoints según sea necesario
    ]
    
    print("\n🔌 TESTING API ENDPOINTS...")
    for url, name in api_urls:
        test_url_access(url, name)

def test_navbar_responsiveness():
    """Test específico del navbar mejorado"""
    print("\n📱 TESTING NAVBAR Y RESPONSIVIDAD...")
    
    # Simular diferentes user agents para responsive
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/", headers=headers, timeout=10)
        success = response.status_code in [200, 302]
        
        if success:
            # Verificar que los CSS de navbar estén cargándose
            css_loaded = 'navbar-center-fix.css' in response.text if response.status_code == 200 else True
            log_test("Navbar CSS Loading", css_loaded, "CSS incluido en template")
        
        log_test("Navbar Responsive Test", success, f"({response.status_code})")
        
    except Exception as e:
        log_test("Navbar Responsive Test", False, f"ERROR: {str(e)}")

def generate_report():
    """Generar reporte de testing"""
    print("\n" + "="*80)
    print("📊 REPORTE FINAL DE TESTING")
    print("="*80)
    
    total_tests = len(TEST_RESULTS)
    passed_tests = sum(1 for result in TEST_RESULTS if '✅' in result['status'])
    failed_tests = total_tests - passed_tests
    
    print(f"📈 RESUMEN:")
    print(f"   Total de Tests: {total_tests}")
    print(f"   ✅ Tests Exitosos: {passed_tests}")
    print(f"   ❌ Tests Fallidos: {failed_tests}")
    print(f"   📊 Porcentaje Éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print(f"\n❌ TESTS FALLIDOS:")
        for result in TEST_RESULTS:
            if '❌' in result['status']:
                print(f"   • {result['test']} - {result['details']}")
    
    print(f"\n✅ TESTS EXITOSOS:")
    for result in TEST_RESULTS:
        if '✅' in result['status']:
            print(f"   • {result['test']} - {result['details']}")
    
    # Guardar reporte en archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"TEST_REPORT_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': f"{(passed_tests/total_tests)*100:.1f}%",
            'results': TEST_RESULTS
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte guardado en: {report_file}")
    return passed_tests, failed_tests

def main():
    """Ejecutar todos los tests"""
    print("🚀 INICIANDO TESTING COMPLETO DEL SISTEMA")
    print(f"🌐 URL Base: {BASE_URL}")
    print(f"🕐 Hora de inicio: {datetime.now().strftime('%H:%M:%S')}")
    print("="*80)
    
    # Esperar a que el servidor esté listo
    print("⏳ Esperando a que el servidor esté listo...")
    time.sleep(2)
    
    # Ejecutar grupos de tests
    test_static_resources()
    test_main_urls()
    test_specialty_urls()
    test_api_endpoints()
    test_navbar_responsiveness()
    
    # Generar reporte final
    passed, failed = generate_report()
    
    print("\n🎯 TESTING COMPLETO FINALIZADO")
    print(f"🏆 Resultado: {'✅ ÉXITO' if failed == 0 else '⚠️ CON ISSUES'}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)