from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from specialties.models import Specialty, Doctor, SpecialtyProcedure
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Carga datos de ejemplo para el módulo de especialidades médicas'

    def handle(self, *args, **options):
        self.stdout.write('Cargando datos de ejemplo para especialidades médicas...')
        
        # Crear especialidades básicas
        specialties_data = [
            {
                'name': 'Medicina General',
                'code': 'MGEN',
                'description': 'Atención médica integral para adultos y familias',
                'consultation_price': Decimal('150.00'),
                'follow_up_price': Decimal('100.00'),
                'requires_referral': False,
            },
            {
                'name': 'Pediatría',
                'code': 'PEDI',
                'description': 'Atención médica especializada para niños y adolescentes',
                'consultation_price': Decimal('180.00'),
                'follow_up_price': Decimal('120.00'),
                'requires_referral': False,
            },
            {
                'name': 'Cardiología',
                'code': 'CARD',
                'description': 'Diagnóstico y tratamiento de enfermedades del corazón',
                'consultation_price': Decimal('250.00'),
                'follow_up_price': Decimal('180.00'),
                'requires_referral': True,
            },
            {
                'name': 'Ginecología',
                'code': 'GINE',
                'description': 'Salud reproductiva y ginecológica femenina',
                'consultation_price': Decimal('200.00'),
                'follow_up_price': Decimal('150.00'),
                'requires_referral': False,
            },
            {
                'name': 'Oftalmología',
                'code': 'OPHT',
                'description': 'Diagnóstico y tratamiento de enfermedades oculares',
                'consultation_price': Decimal('220.00'),
                'follow_up_price': Decimal('160.00'),
                'requires_referral': True,
            },
            {
                'name': 'Odontología',
                'code': 'DENT',
                'description': 'Salud bucodental y tratamientos dentales',
                'consultation_price': Decimal('120.00'),
                'follow_up_price': Decimal('80.00'),
                'requires_referral': False,
            },
            {
                'name': 'Nutrición',
                'code': 'NUTR',
                'description': 'Evaluación nutricional y planes alimentarios',
                'consultation_price': Decimal('160.00'),
                'follow_up_price': Decimal('110.00'),
                'requires_referral': False,
            },
            {
                'name': 'Psicología',
                'code': 'PSYC',
                'description': 'Evaluación y tratamiento psicológico',
                'consultation_price': Decimal('180.00'),
                'follow_up_price': Decimal('140.00'),
                'requires_referral': False,
            },
            {
                'name': 'Dermatología',
                'code': 'DERM',
                'description': 'Diagnóstico y tratamiento de enfermedades de la piel',
                'consultation_price': Decimal('200.00'),
                'follow_up_price': Decimal('150.00'),
                'requires_referral': True,
            },
            {
                'name': 'Neurología',
                'code': 'NEUR',
                'description': 'Diagnóstico y tratamiento de enfermedades del sistema nervioso',
                'consultation_price': Decimal('280.00'),
                'follow_up_price': Decimal('200.00'),
                'requires_referral': True,
            },
            {
                'name': 'Traumatología',
                'code': 'TRAU',
                'description': 'Diagnóstico y tratamiento de fracturas y lesiones osteoarticulares',
                'consultation_price': Decimal('230.00'),
                'follow_up_price': Decimal('170.00'),
                'requires_referral': True,
            },
        ]
        
        created_specialties = []
        for spec_data in specialties_data:
            specialty, created = Specialty.objects.get_or_create(
                code=spec_data['code'],
                defaults=spec_data
            )
            if created:
                created_specialties.append(specialty)
                self.stdout.write(f'  + Creada especialidad: {specialty.name}')
            else:
                self.stdout.write(f'  - Ya existe: {specialty.name}')
        
        # Crear procedimientos de ejemplo para algunas especialidades
        procedures_data = [
            # Cardiología
            {
                'specialty_code': 'CARD',
                'procedures': [
                    {
                        'name': 'Electrocardiograma (ECG)',
                        'description': 'Registro de la actividad eléctrica del corazón',
                        'duration_minutes': 30,
                        'price': Decimal('80.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Ecocardiograma',
                        'description': 'Ultrasonido del corazón para evaluar estructura y función',
                        'duration_minutes': 45,
                        'price': Decimal('150.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Holter 24 horas',
                        'description': 'Monitoreo continuo del ritmo cardíaco por 24 horas',
                        'duration_minutes': 30,
                        'price': Decimal('200.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                ]
            },
            # Oftalmología
            {
                'specialty_code': 'OPHT',
                'procedures': [
                    {
                        'name': 'Examen de Fondo de Ojo',
                        'description': 'Evaluación de la retina y estructuras oculares',
                        'duration_minutes': 30,
                        'price': Decimal('100.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Tonometría',
                        'description': 'Medición de la presión intraocular',
                        'duration_minutes': 15,
                        'price': Decimal('60.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Campo Visual',
                        'description': 'Evaluación del campo visual periférico',
                        'duration_minutes': 45,
                        'price': Decimal('120.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                ]
            },
            # Odontología
            {
                'specialty_code': 'DENT',
                'procedures': [
                    {
                        'name': 'Limpieza Dental',
                        'description': 'Profilaxis y limpieza dental profesional',
                        'duration_minutes': 60,
                        'price': Decimal('80.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Empaste Dental',
                        'description': 'Restauración de caries con resina compuesta',
                        'duration_minutes': 45,
                        'price': Decimal('120.00'),
                        'requires_anesthesia': True,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Extracción Dental',
                        'description': 'Extracción de pieza dental dañada',
                        'duration_minutes': 30,
                        'price': Decimal('150.00'),
                        'requires_anesthesia': True,
                        'requires_fasting': False,
                    },
                ]
            },
            # Ginecología
            {
                'specialty_code': 'GINE',
                'procedures': [
                    {
                        'name': 'Papanicolaou',
                        'description': 'Estudio citológico para detección de cáncer cervical',
                        'duration_minutes': 20,
                        'price': Decimal('70.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Ultrasonido Pélvico',
                        'description': 'Ultrasonido de órganos reproductivos femeninos',
                        'duration_minutes': 30,
                        'price': Decimal('100.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Colposcopía',
                        'description': 'Examen detallado del cuello uterino',
                        'duration_minutes': 45,
                        'price': Decimal('180.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                ]
            },
            # Traumatología
            {
                'specialty_code': 'TRAU',
                'procedures': [
                    {
                        'name': 'Radiografía Simple',
                        'description': 'Radiografía de huesos y articulaciones',
                        'duration_minutes': 15,
                        'price': Decimal('60.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Inmovilización con Yeso',
                        'description': 'Colocación de yeso para fracturas',
                        'duration_minutes': 45,
                        'price': Decimal('120.00'),
                        'requires_anesthesia': False,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Infiltración Articular',
                        'description': 'Infiltración con corticoides en articulaciones',
                        'duration_minutes': 30,
                        'price': Decimal('180.00'),
                        'requires_anesthesia': True,
                        'requires_fasting': False,
                    },
                    {
                        'name': 'Reducción de Fractura',
                        'description': 'Reducción cerrada de fractura simple',
                        'duration_minutes': 60,
                        'price': Decimal('300.00'),
                        'requires_anesthesia': True,
                        'requires_fasting': True,
                    },
                ]
            },
        ]
        
        created_procedures = 0
        for proc_group in procedures_data:
            try:
                specialty = Specialty.objects.get(code=proc_group['specialty_code'])
                for proc_data in proc_group['procedures']:
                    proc_data['specialty'] = specialty
                    procedure, created = SpecialtyProcedure.objects.get_or_create(
                        name=proc_data['name'],
                        specialty=specialty,
                        defaults=proc_data
                    )
                    if created:
                        created_procedures += 1
                        self.stdout.write(f'  + Creado procedimiento: {procedure.name} ({specialty.name})')
            except Specialty.DoesNotExist:
                self.stdout.write(f'  ! Especialidad no encontrada: {proc_group["specialty_code"]}')
        
        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'EXITO: Datos cargados exitosamente:')
        self.stdout.write(f'   - Especialidades creadas: {len(created_specialties)}')
        self.stdout.write(f'   - Procedimientos creados: {created_procedures}')
        self.stdout.write(f'   - Total especialidades en sistema: {Specialty.objects.count()}')
        self.stdout.write(f'   - Total procedimientos en sistema: {SpecialtyProcedure.objects.count()}')
        self.stdout.write('='*50)
        
        # Notas adicionales
        self.stdout.write('\nNotas importantes:')
        self.stdout.write('   - Para asignar doctores a especialidades, use el admin de Django')
        self.stdout.write('   - Los precios pueden ser ajustados según su región')
        self.stdout.write('   - Agregue más procedimientos según las necesidades de su clínica')
        
        self.stdout.write(self.style.SUCCESS('\nProceso completado exitosamente!'))