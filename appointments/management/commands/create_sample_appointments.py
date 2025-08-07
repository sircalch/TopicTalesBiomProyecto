from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from appointments.models import Appointment, AppointmentType, DoctorSchedule
from accounts.models import User
from patients.models import Patient
from accounts.models import Organization
import random


class Command(BaseCommand):
    help = 'Create sample appointments and schedules for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample appointments and schedules...')
        
        try:
            # Get the first organization
            organization = Organization.objects.first()
            if not organization:
                self.stdout.write(self.style.ERROR('No organization found. Please create an organization first.'))
                return
            
            # Get or create doctors
            doctors = User.objects.filter(
                profile__organization=organization,
                role='doctor',
                is_active=True
            )
            
            if not doctors.exists():
                self.stdout.write(self.style.ERROR('No doctors found. Please create doctors first.'))
                return
            
            # Get or create patients
            patients = Patient.objects.filter(
                organization=organization,
                is_active=True
            )
            
            if not patients.exists():
                self.stdout.write(self.style.ERROR('No patients found. Please create patients first.'))
                return
            
            # Get or create appointment types
            appointment_types = AppointmentType.objects.filter(
                organization=organization,
                is_active=True
            )
            
            if not appointment_types.exists():
                # Create default appointment types
                AppointmentType.objects.create(
                    name="Consulta General",
                    description="Consulta médica general",
                    duration_minutes=30,
                    color="#007bff",
                    price=500.00,
                    organization=organization
                )
                AppointmentType.objects.create(
                    name="Consulta de Seguimiento",
                    description="Consulta de seguimiento",
                    duration_minutes=20,
                    color="#28a745",
                    price=300.00,
                    organization=organization
                )
                AppointmentType.objects.create(
                    name="Consulta de Emergencia",
                    description="Consulta de emergencia",
                    duration_minutes=45,
                    color="#dc3545",
                    price=800.00,
                    organization=organization
                )
                appointment_types = AppointmentType.objects.filter(organization=organization, is_active=True)
            
            # Create doctor schedules if they don't exist
            self.create_doctor_schedules(doctors, organization)
            
            # Create sample appointments for today and this week
            self.create_sample_appointments(doctors, patients, appointment_types, organization)
            
            self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating sample data: {str(e)}'))
    
    def create_doctor_schedules(self, doctors, organization):
        """Create sample schedules for doctors"""
        for doctor in doctors:
            # Check if doctor already has schedules
            if DoctorSchedule.objects.filter(doctor=doctor).exists():
                continue
            
            # Create Monday to Friday schedule
            for day in range(5):  # 0=Monday, 4=Friday
                DoctorSchedule.objects.create(
                    doctor=doctor,
                    organization=organization,
                    day_of_week=day,
                    start_time=time(8, 0),  # 8:00 AM
                    end_time=time(17, 0),   # 5:00 PM
                    break_start=time(12, 0), # 12:00 PM
                    break_end=time(13, 0),   # 1:00 PM
                    is_active=True
                )
            
            self.stdout.write(f'Created schedule for Dr. {doctor.get_full_name()}')
    
    def create_sample_appointments(self, doctors, patients, appointment_types, organization):
        """Create sample appointments"""
        today = timezone.now().date()
        
        # Create appointments for today
        self.create_appointments_for_date(today, doctors, patients, appointment_types, organization, 8)
        
        # Create appointments for tomorrow
        tomorrow = today + timedelta(days=1)
        self.create_appointments_for_date(tomorrow, doctors, patients, appointment_types, organization, 6)
        
        # Create appointments for the rest of the week
        for i in range(2, 7):
            future_date = today + timedelta(days=i)
            self.create_appointments_for_date(future_date, doctors, patients, appointment_types, organization, 4)
        
        # Create some past appointments (completed)
        for i in range(1, 4):
            past_date = today - timedelta(days=i)
            self.create_appointments_for_date(past_date, doctors, patients, appointment_types, organization, 3, status='completed')
    
    def create_appointments_for_date(self, date, doctors, patients, appointment_types, organization, count, status='scheduled'):
        """Create appointments for a specific date"""
        start_times = [
            time(9, 0), time(9, 30), time(10, 0), time(10, 30),
            time(11, 0), time(11, 30), time(14, 0), time(14, 30),
            time(15, 0), time(15, 30), time(16, 0), time(16, 30)
        ]
        
        reasons = [
            "Dolor de cabeza frecuente",
            "Control de presión arterial",
            "Revisión médica general",
            "Seguimiento de tratamiento",
            "Dolor abdominal",
            "Control de diabetes",
            "Consulta por gripe",
            "Examen médico ocupacional",
            "Control de medicación",
            "Consulta por dolor de espalda"
        ]
        
        used_times = {}  # Track used times per doctor
        
        for i in range(min(count, len(patients))):
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            appointment_type = random.choice(appointment_types)
            
            # Ensure no conflicts per doctor
            if doctor.id not in used_times:
                used_times[doctor.id] = []
            
            available_times = [t for t in start_times if t not in used_times[doctor.id]]
            if not available_times:
                continue
            
            start_time = random.choice(available_times)
            used_times[doctor.id].append(start_time)
            
            start_datetime = timezone.make_aware(
                datetime.combine(date, start_time)
            )
            end_datetime = start_datetime + timedelta(minutes=appointment_type.duration_minutes)
            
            # Random status for future appointments
            if status == 'scheduled' and date > timezone.now().date():
                appointment_status = random.choice(['scheduled', 'confirmed'])
            else:
                appointment_status = status
            
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_type=appointment_type,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                reason=random.choice(reasons),
                status=appointment_status,
                priority=random.choice(['normal', 'normal', 'normal', 'high', 'low']),  # More normal priority
                organization=organization,
                created_by=doctor,
                patient_phone=patient.phone_number,
                patient_email=patient.email
            )
        
        self.stdout.write(f'Created {min(count, len(patients))} appointments for {date}')