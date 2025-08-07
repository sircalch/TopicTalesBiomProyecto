from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Organization
from patients.models import Patient, MedicalHistory, VitalSigns
from datetime import date, datetime
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Carga pacientes de muestra para pruebas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Número de pacientes a crear (por defecto: 10)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Obtener la primera organización disponible
        try:
            organization = Organization.objects.first()
            if not organization:
                self.stdout.write(
                    self.style.ERROR('No hay organizaciones disponibles. Crea una organización primero.')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al obtener organización: {e}')
            )
            return

        # Obtener el primer usuario disponible para asignar como creador
        try:
            user = User.objects.first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('No hay usuarios disponibles. Crea un usuario primero.')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al obtener usuario: {e}')
            )
            return

        # Datos de muestra
        nombres = [
            ('Maria', 'Gonzalez', 'Lopez'),
            ('Juan', 'Rodriguez', 'Martinez'),
            ('Ana', 'Hernandez', 'Garcia'),
            ('Carlos', 'Lopez', 'Sanchez'),
            ('Elena', 'Martinez', 'Fernandez'),
            ('Miguel', 'Sanchez', 'Diaz'),
            ('Carmen', 'Diaz', 'Ruiz'),
            ('Antonio', 'Fernandez', 'Moreno'),
            ('Isabel', 'Ruiz', 'Jimenez'),
            ('Jose', 'Moreno', 'Alvarez'),
            ('Patricia', 'Jimenez', 'Romero'),
            ('Francisco', 'Alvarez', 'Torres'),
            ('Lucia', 'Romero', 'Ramos'),
            ('Manuel', 'Torres', 'Vazquez'),
            ('Cristina', 'Ramos', 'Castro')
        ]

        tipos_sangre = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        generos = ['M', 'F']
        estados_civiles = ['single', 'married', 'divorced', 'widowed']

        pacientes_creados = 0
        base_patient_count = Patient.objects.count()

        for i in range(count):
            # Seleccionar datos aleatorios
            nombre_data = random.choice(nombres)
            nombre, apellido_paterno, apellido_materno = nombre_data
            
            # Generar fecha de nacimiento (18-80 años)
            edad = random.randint(18, 80)
            fecha_nacimiento = date(2024 - edad, random.randint(1, 12), random.randint(1, 28))
            
            # Generar ID único basado en el conteo actual más el índice
            patient_id = f"PAC{str(base_patient_count + i + 1).zfill(3)}"
            
            # Verificar que el ID no exista ya
            while Patient.objects.filter(patient_id=patient_id).exists():
                base_patient_count += 1
                patient_id = f"PAC{str(base_patient_count + i + 1).zfill(3)}"
            
            try:
                # Crear paciente
                paciente = Patient.objects.create(
                    patient_id=patient_id,
                    first_name=nombre,
                    last_name=apellido_paterno,
                    mother_last_name=apellido_materno,
                    birth_date=fecha_nacimiento,
                    gender=random.choice(generos),
                    phone_number=f"+52 55 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    email=f"{nombre.lower()}.{apellido_paterno.lower()}@ejemplo.com",
                    address=f"Calle {random.randint(1, 100)} #{random.randint(1, 999)}",
                    city="Ciudad de México" if random.random() > 0.3 else random.choice([
                        "Guadalajara", "Monterrey", "Puebla", "Toluca", "Tijuana"
                    ]),
                    state="CDMX" if random.random() > 0.3 else random.choice([
                        "Jalisco", "Nuevo León", "Puebla", "Estado de México", "Baja California"
                    ]),
                    postal_code=f"{random.randint(10000, 99999)}",
                    blood_type=random.choice(tipos_sangre),
                    weight=round(random.uniform(50.0, 120.0), 1),
                    height=round(random.uniform(150.0, 190.0), 1),
                    marital_status=random.choice(estados_civiles),
                    occupation=random.choice([
                        "Ingeniero", "Docente", "Comerciante", "Estudiante", "Jubilado",
                        "Médico", "Abogado", "Contador", "Administrador", "Otros"
                    ]),
                    emergency_contact_name=f"Familiar de {nombre}",
                    emergency_contact_relationship=random.choice([
                        "Esposo/a", "Hijo/a", "Madre", "Padre", "Hermano/a"
                    ]),
                    emergency_contact_phone=f"+52 55 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    organization=organization,
                    created_by=user,
                    notes=f"Paciente de muestra #{i+1}"
                )

                # Crear historia médica básica
                if random.random() > 0.3:  # 70% de probabilidad
                    MedicalHistory.objects.create(
                        patient=paciente,
                        allergies=random.choice([
                            "",
                            "Penicilina",
                            "Mariscos",
                            "Polen",
                            "Lácteos",
                            "Ninguna conocida"
                        ]) if random.random() > 0.5 else "",
                        chronic_diseases=random.choice([
                            "",
                            "Hipertensión",
                            "Diabetes Tipo 2",
                            "Asma",
                            "Artritis",
                            "Ninguna"
                        ]) if random.random() > 0.7 else "",
                        smoking_status=random.choice(['never', 'former', 'current', 'occasional']),
                        alcohol_consumption=random.choice(['none', 'occasional', 'moderate']),
                        exercise_frequency=random.choice(['none', 'light', 'moderate', 'intense']),
                        updated_by=user
                    )

                # Crear signos vitales recientes
                if random.random() > 0.4:  # 60% de probabilidad
                    VitalSigns.objects.create(
                        patient=paciente,
                        systolic_pressure=random.randint(110, 140),
                        diastolic_pressure=random.randint(70, 90),
                        heart_rate=random.randint(60, 100),
                        respiratory_rate=random.randint(12, 20),
                        temperature=round(random.uniform(36.0, 37.5), 1),
                        oxygen_saturation=random.randint(95, 100),
                        weight=paciente.weight,
                        height=paciente.height,
                        glucose_level=random.randint(70, 120) if random.random() > 0.5 else None,
                        recorded_by=user,
                        notes="Signos vitales de muestra"
                    )

                pacientes_creados += 1
                self.stdout.write(f"Paciente creado: {paciente.get_full_name()} (ID: {patient_id})")

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creando paciente {nombre} {apellido_paterno}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSe crearon {pacientes_creados} pacientes exitosamente!')
        )
        
        if pacientes_creados > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Total de pacientes en el sistema: {Patient.objects.count()}')
            )