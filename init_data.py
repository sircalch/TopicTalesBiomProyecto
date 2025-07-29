#!/usr/bin/env python
"""
Script para inicializar datos de prueba en TopicTales Biomédica
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topictales_biomedica.settings')
django.setup()

from accounts.models import User, Organization, Subscription, UserProfile
from patients.models import Patient, MedicalHistory
from appointments.models import AppointmentType, Appointment

def create_demo_data():
    """Create demo data for TopicTales Biomédica"""
    
    print("Creando datos de demostracion para TopicTales Biomedica...")
    
    # 1. Create Organization
    print("Creando organizacion...")
    organization, created = Organization.objects.get_or_create(
        name="Clínica San Rafael",
        defaults={
            'legal_name': "Clínica San Rafael S.A. de C.V.",
            'tax_id': "CSR123456789",
            'address': "Av. Reforma 123, Col. Centro, CDMX",
            'phone': "+52 55 1234-5678",
            'email': "contacto@clinicasanrafael.com",
            'website': "https://clinicasanrafael.com",
            'director_name': "Dr. Rafael Sánchez",
            'director_license': "12345678"
        }
    )
    
    # 2. Create Subscription
    print("Creando suscripcion...")
    subscription, created = Subscription.objects.get_or_create(
        organization=organization,
        defaults={
            'plan': 'ADVANCED',
            'status': 'active',
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=365),
            'trial_end_date': timezone.now() + timedelta(days=30),
            'max_patients': -1,  # Unlimited
            'max_users': -1,     # Unlimited
            'monthly_price': 2500.00,
            'currency': 'MXN'
        }
    )
    
    # 3. Create Admin User
    print("Creando usuario administrador...")
    admin_user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            'email': "admin@clinicasanrafael.com",
            'first_name': "Administrador",
            'last_name': "Sistema",
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'phone_number': "+52 55 1234-5678",
            'professional_license': "ADM123456"
        }
    )
    if created:
        admin_user.set_password("admin123")
        admin_user.save()
    
    # 4. Create Admin Profile
    profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'organization': organization,
            'department': "Administración",
            'position': "Administrador del Sistema"
        }
    )
    
    # 5. Create Doctor User
    print("Creando usuario medico...")
    doctor_user, created = User.objects.get_or_create(
        username="doctor",
        defaults={
            'email': "doctor@clinicasanrafael.com",
            'first_name': "Dr. María",
            'last_name': "García López",
            'role': 'doctor',
            'phone_number': "+52 55 9876-5432",
            'professional_license': "MED123456",
            'specialty': "Medicina General"
        }
    )
    if created:
        doctor_user.set_password("doctor123")
        doctor_user.save()
    
    # 6. Create Doctor Profile
    doctor_profile, created = UserProfile.objects.get_or_create(
        user=doctor_user,
        defaults={
            'organization': organization,
            'department': "Medicina General",
            'position': "Médico General"
        }
    )
    
    # 7. Create Receptionist User
    print("Creando usuario recepcionista...")
    receptionist_user, created = User.objects.get_or_create(
        username="recepcion",
        defaults={
            'email': "recepcion@clinicasanrafael.com",
            'first_name': "Ana",
            'last_name': "Martínez",
            'role': 'receptionist',
            'phone_number': "+52 55 5555-1234"
        }
    )
    if created:
        receptionist_user.set_password("recepcion123")
        receptionist_user.save()
    
    # 8. Create Receptionist Profile
    receptionist_profile, created = UserProfile.objects.get_or_create(
        user=receptionist_user,
        defaults={
            'organization': organization,
            'department': "Recepción",
            'position': "Recepcionista"
        }
    )
    
    # 9. Create Sample Patients
    print("Creando pacientes de ejemplo...")
    patients_data = [
        {
            'patient_id': 'PAC001',
            'first_name': 'Juan Carlos',
            'last_name': 'Pérez',
            'mother_last_name': 'González',
            'birth_date': '1985-03-15',
            'gender': 'M',
            'phone_number': '+52 55 1111-2222',
            'email': 'juan.perez@email.com',
            'address': 'Calle Morelos 456, Col. Centro',
            'city': 'México',
            'state': 'CDMX',
            'postal_code': '01000',
            'blood_type': 'O+',
            'emergency_contact_name': 'María Pérez',
            'emergency_contact_relationship': 'Esposa',
            'emergency_contact_phone': '+52 55 2222-1111'
        },
        {
            'patient_id': 'PAC002',
            'first_name': 'María Isabel',
            'last_name': 'López',
            'mother_last_name': 'Hernández',
            'birth_date': '1990-07-22',
            'gender': 'F',
            'phone_number': '+52 55 3333-4444',
            'email': 'maria.lopez@email.com',
            'address': 'Av. Insurgentes 789, Col. Roma',
            'city': 'México',
            'state': 'CDMX',
            'postal_code': '06700',
            'blood_type': 'A+',
            'emergency_contact_name': 'Carlos López',
            'emergency_contact_relationship': 'Hermano',
            'emergency_contact_phone': '+52 55 4444-3333'
        },
        {
            'patient_id': 'PAC003',
            'first_name': 'Luis Miguel',
            'last_name': 'Rodríguez',
            'mother_last_name': 'Sánchez',
            'birth_date': '1978-11-08',
            'gender': 'M',
            'phone_number': '+52 55 5555-6666',
            'email': 'luis.rodriguez@email.com',
            'address': 'Calle Juárez 321, Col. Doctores',
            'city': 'México',
            'state': 'CDMX',
            'postal_code': '06720',
            'blood_type': 'B+',
            'emergency_contact_name': 'Carmen Rodríguez',
            'emergency_contact_relationship': 'Madre',
            'emergency_contact_phone': '+52 55 6666-5555'
        }
    ]
    
    for patient_data in patients_data:
        patient_data['birth_date'] = datetime.strptime(patient_data['birth_date'], '%Y-%m-%d').date()
        patient, created = Patient.objects.get_or_create(
            patient_id=patient_data['patient_id'],
            defaults={
                **patient_data,
                'organization': organization,
                'created_by': admin_user
            }
        )
        
        # Create medical history for each patient
        if created:
            MedicalHistory.objects.create(
                patient=patient,
                allergies="Ninguna conocida",
                chronic_diseases="Ninguna",
                smoking_status="never",
                alcohol_consumption="none",
                exercise_frequency="moderate",
                updated_by=doctor_user
            )
    
    # 10. Create Appointment Types
    print("Creando tipos de citas...")
    appointment_types_data = [
        {'name': 'Consulta General', 'duration_minutes': 30, 'color': '#007bff', 'price': 500.00},
        {'name': 'Consulta de Seguimiento', 'duration_minutes': 20, 'color': '#28a745', 'price': 300.00},
        {'name': 'Consulta Urgente', 'duration_minutes': 15, 'color': '#dc3545', 'price': 800.00},
        {'name': 'Revisión Anual', 'duration_minutes': 45, 'color': '#6f42c1', 'price': 750.00},
        {'name': 'Consulta Nutricional', 'duration_minutes': 40, 'color': '#fd7e14', 'price': 600.00}
    ]
    
    for apt_type_data in appointment_types_data:
        AppointmentType.objects.get_or_create(
            name=apt_type_data['name'],
            organization=organization,
            defaults=apt_type_data
        )
    
    # 11. Create Sample Appointments
    print("Creando citas de ejemplo...")
    patients = Patient.objects.filter(organization=organization)
    appointment_types = AppointmentType.objects.filter(organization=organization)
    
    today = timezone.now().date()
    
    # Today's appointments
    for i, patient in enumerate(patients[:2]):
        start_time = timezone.now().replace(hour=10+i*2, minute=0, second=0, microsecond=0)
        appointment_type = appointment_types[i % len(appointment_types)]
        
        Appointment.objects.get_or_create(
            patient=patient,
            doctor=doctor_user,
            start_datetime=start_time,
            defaults={
                'appointment_type': appointment_type,
                'end_datetime': start_time + timedelta(minutes=appointment_type.duration_minutes),
                'reason': f'Consulta de control - {patient.get_full_name()}',
                'status': 'confirmed',
                'organization': organization,
                'created_by': receptionist_user
            }
        )
    
    # Future appointments
    for i in range(5):
        future_date = timezone.now() + timedelta(days=i+1)
        start_time = future_date.replace(hour=9+i, minute=0, second=0, microsecond=0)
        patient = patients[i % len(patients)]
        appointment_type = appointment_types[i % len(appointment_types)]
        
        Appointment.objects.get_or_create(
            patient=patient,
            doctor=doctor_user,
            start_datetime=start_time,
            defaults={
                'appointment_type': appointment_type,
                'end_datetime': start_time + timedelta(minutes=appointment_type.duration_minutes),
                'reason': f'Cita programada - {patient.get_full_name()}',
                'status': 'scheduled',
                'organization': organization,
                'created_by': receptionist_user
            }
        )
    
    print("\nDatos de demostracion creados exitosamente!")
    print("\nCredenciales de acceso:")
    print("=" * 50)
    print("ADMINISTRADOR:")
    print("   Usuario: admin")
    print("   Password: admin123")
    print("\nMEDICO:")
    print("   Usuario: doctor")
    print("   Password: doctor123")
    print("\nRECEPCIONISTA:")
    print("   Usuario: recepcion")
    print("   Password: recepcion123")
    print("=" * 50)
    print("\nPara acceder al sistema:")
    print("1. Ejecuta: python manage.py runserver")
    print("2. Abre tu navegador en: http://localhost:8000")
    print("3. Usa cualquiera de las credenciales de arriba")
    print("\nTopicTales Biomedica esta listo para usar!")

if __name__ == "__main__":
    create_demo_data()