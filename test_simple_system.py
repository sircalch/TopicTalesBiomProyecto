#!/usr/bin/env python
"""
TEST SISTEMA SIMPLE - TopicTales Biomedica
Testing basico de funcionalidades principales
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8004"

def test_url(url_path, name):
    """Probar una URL"""
    try:
        response = requests.get(f"{BASE_URL}{url_path}", timeout=5)
        status = "PASS" if response.status_code in [200, 302] else "FAIL"
        print(f"{status} - {name} ({response.status_code})")
        return response.status_code in [200, 302]
    except Exception as e:
        print(f"FAIL - {name} (ERROR: {str(e)})")
        return False

def main():
    print("TESTING SISTEMA COMPLETO")
    print("=" * 50)
    print(f"URL Base: {BASE_URL}")
    print(f"Hora: {datetime.now().strftime('%H:%M:%S')}")
    print("")
    
    # Esperar servidor
    print("Esperando servidor...")
    time.sleep(2)
    
    tests_passed = 0
    tests_total = 0
    
    # Tests principales
    print("TESTING URLs PRINCIPALES:")
    urls = [
        ('/', 'Home Page'),
        ('/dashboard/', 'Dashboard'),
        ('/patients/', 'Patients'),
        ('/patients/create/', 'Create Patient'),
        ('/appointments/', 'Appointments'),
        ('/specialties/', 'Specialties'),
        ('/accounts/login/', 'Login'),
    ]
    
    for url, name in urls:
        if test_url(url, name):
            tests_passed += 1
        tests_total += 1
    
    print("")
    print("TESTING ESPECIALIDADES:")
    specialties = [
        ('/specialties/cardiology/', 'Cardiologia'),
        ('/specialties/pediatrics/', 'Pediatria'),
        ('/specialties/gynecology/', 'Ginecologia'),
    ]
    
    for url, name in specialties:
        if test_url(url, name):
            tests_passed += 1
        tests_total += 1
    
    print("")
    print("TESTING RECURSOS ESTATICOS:")
    static_resources = [
        ('/static/css/navbar-center-fix.css', 'Navbar CSS'),
        ('/static/js/navbar-sidebar-sync.js', 'Navbar JS'),
    ]
    
    for url, name in static_resources:
        if test_url(url, name):
            tests_passed += 1
        tests_total += 1
    
    # Reporte final
    print("")
    print("=" * 50)
    print("REPORTE FINAL")
    print("=" * 50)
    print(f"Tests ejecutados: {tests_total}")
    print(f"Tests exitosos: {tests_passed}")
    print(f"Tests fallidos: {tests_total - tests_passed}")
    print(f"Porcentaje exito: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("RESULTADO: TODOS LOS TESTS PASARON!")
    else:
        print("RESULTADO: ALGUNOS TESTS FALLARON")
    
    return tests_passed == tests_total

if __name__ == "__main__":
    success = main()
    print(f"\nTest completado: {'EXITO' if success else 'CON ERRORES'}")