#!/usr/bin/env python
"""
Test de funcionalidades de exportacion
Verificar que Excel, PDF y CSV funcionen correctamente
"""

import requests
import os
from datetime import datetime

BASE_URL = "http://127.0.0.1:8004"

def test_export(export_type, url_path):
    """Probar una exportacion especifica"""
    try:
        print(f"Testing {export_type} export...")
        response = requests.get(f"{BASE_URL}{url_path}", timeout=30)
        
        # Verificar codigo de respuesta
        if response.status_code != 200:
            print(f"FAIL - {export_type}: HTTP {response.status_code}")
            return False
        
        # Verificar content type
        content_type = response.headers.get('content-type', '')
        expected_types = {
            'Excel': 'application/vnd.openxmlformats',
            'PDF': 'application/pdf',
            'CSV': 'text/csv'
        }
        
        if export_type in expected_types and expected_types[export_type] not in content_type:
            print(f"FAIL - {export_type}: Wrong content type: {content_type}")
            return False
        
        # Verificar que tenga contenido
        content_length = len(response.content)
        if content_length < 100:  # Archivo muy pequeño, probablemente error
            print(f"FAIL - {export_type}: File too small ({content_length} bytes)")
            return False
        
        print(f"PASS - {export_type}: {content_length} bytes, {content_type}")
        return True
        
    except Exception as e:
        print(f"FAIL - {export_type}: {str(e)}")
        return False

def main():
    print("TESTING FUNCIONALIDADES DE EXPORTACION")
    print("=" * 60)
    print(f"URL Base: {BASE_URL}")
    print(f"Hora: {datetime.now().strftime('%H:%M:%S')}")
    print("")
    
    # Tests de exportacion de pacientes
    export_tests = [
        ('Excel', '/patients/export/excel/'),
        ('PDF', '/patients/export/pdf/'),  
        ('CSV', '/patients/export/csv/'),
    ]
    
    results = []
    for export_type, url in export_tests:
        success = test_export(export_type, url)
        results.append((export_type, success))
    
    # Reporte final
    print("")
    print("=" * 60)
    print("REPORTE EXPORTACIONES")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for export_type, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status} - Export {export_type}")
    
    print("")
    print(f"Total: {total_tests}")
    print(f"Exitosos: {passed_tests}")
    print(f"Fallidos: {total_tests - passed_tests}")
    print(f"Porcentaje: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("RESULTADO: TODAS LAS EXPORTACIONES FUNCIONAN!")
    else:
        print("RESULTADO: ALGUNAS EXPORTACIONES TIENEN PROBLEMAS")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    print(f"\nExportaciones test: {'EXITO' if success else 'CON ERRORES'}")