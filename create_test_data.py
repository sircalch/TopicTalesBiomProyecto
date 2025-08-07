#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from django.contrib.auth import get_user_model
from equipment.models import EquipmentCategory, Location, Supplier
from billing.models import Service

User = get_user_model()

def create_equipment_data():
    """Crear datos básicos para el módulo de equipos"""
    print("Creando datos para el módulo de equipos...")
    
    # Categorías de equipos
    categories = [
        {"name": "Equipos de Diagnóstico", "description": "Equipos para diagnóstico médico"},
        {"name": "Equipos Quirúrgicos", "description": "Instrumentos para cirugía"},
        {"name": "Equipos de Laboratorio", "description": "Equipos de análisis clínico"},
        {"name": "Equipos de Emergencia", "description": "Equipos para emergencias médicas"},
        {"name": "Equipos de Rehabilitación", "description": "Equipos para fisioterapia"},
    ]
    
    for cat_data in categories:
        category, created = EquipmentCategory.objects.get_or_create(
            name=cat_data["name"],
            defaults={"description": cat_data["description"]}
        )
        if created:
            print(f"  + Categoria creada: {category.name}")
    
    # Ubicaciones
    locations = [
        {"name": "Consulta 1", "floor": "1", "room_number": "101"},
        {"name": "Consulta 2", "floor": "1", "room_number": "102"},
        {"name": "Sala de Cirugia", "floor": "2", "room_number": "201"},
        {"name": "Laboratorio", "floor": "1", "room_number": "103"},
        {"name": "Almacen", "floor": "1", "room_number": "104"},
    ]
    
    for loc_data in locations:
        location, created = Location.objects.get_or_create(
            name=loc_data["name"],
            defaults={
                "floor": loc_data["floor"],
                "room_number": loc_data["room_number"]
            }
        )
        if created:
            print(f"  + Ubicacion creada: {location.name}")
    
    # Proveedores
    suppliers = [
        {
            "name": "MedEquip Solutions",
            "contact_person": "Dr. Juan Perez",
            "phone": "+52-555-1234",
            "email": "contacto@medequip.com"
        },
        {
            "name": "Instrumentos Medicos SA",
            "contact_person": "Maria Gonzalez",
            "phone": "+52-555-5678",
            "email": "ventas@instrumentos.com"
        },
        {
            "name": "TecnoMed Ltda",
            "contact_person": "Carlos Rodriguez",
            "phone": "+52-555-9012",
            "email": "info@tecnomed.com"
        }
    ]
    
    for sup_data in suppliers:
        supplier, created = Supplier.objects.get_or_create(
            name=sup_data["name"],
            defaults={
                "contact_person": sup_data["contact_person"],
                "phone": sup_data["phone"],
                "email": sup_data["email"]
            }
        )
        if created:
            print(f"  + Proveedor creado: {supplier.name}")

def create_billing_data():
    """Crear datos basicos para el modulo de facturacion"""
    print("Creando datos para el modulo de facturacion...")
    
    services = [
        {"name": "Consulta Medica General", "code": "CM-001", "price": 500.00, "category": "Consultas"},
        {"name": "Consulta de Especialidad", "code": "CE-001", "price": 800.00, "category": "Consultas"},
        {"name": "Electrocardiograma", "code": "ECG-001", "price": 300.00, "category": "Estudios"},
        {"name": "Analisis de Sangre Completo", "code": "LAB-001", "price": 450.00, "category": "Laboratorio"},
        {"name": "Radiografia de Torax", "code": "RX-001", "price": 600.00, "category": "Imagenologia"},
        {"name": "Consulta Psicologica", "code": "PSI-001", "price": 700.00, "category": "Psicologia"},
        {"name": "Consulta Nutricional", "code": "NUT-001", "price": 650.00, "category": "Nutricion"},
    ]
    
    for serv_data in services:
        service, created = Service.objects.get_or_create(
            code=serv_data["code"],
            defaults={
                "name": serv_data["name"],
                "price": serv_data["price"],
                "category": serv_data["category"]
            }
        )
        if created:
            print(f"  + Servicio creado: {service.name} - ${service.price}")

def main():
    print("TopicTales Biomedica - Creando datos de prueba")
    print("=" * 50)
    
    try:
        create_equipment_data()
        print()
        create_billing_data()
        print()
        print("Datos de prueba creados exitosamente!")
        print("\nAhora puedes acceder a:")
        print("- Equipos: http://127.0.0.1:8000/equipment/")
        print("- Facturacion: http://127.0.0.1:8000/billing/")
        print("- Usuarios: http://127.0.0.1:8000/accounts/users/")
        
    except Exception as e:
        print(f"Error creando datos: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()