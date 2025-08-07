from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import SystemModule


class Command(BaseCommand):
    help = 'Initialize system modules for TopicTales Biomédica'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Inicializando módulos del sistema...')
            
            # Core modules (available in all plans)
            core_modules = [
                {
                    'name': 'dashboard',
                    'display_name': 'Dashboard',
                    'description': 'Panel principal con resumen de actividades',
                    'icon': 'fas fa-tachometer-alt',
                    'url_name': 'dashboard:index',
                    'category': 'core',
                    'order': 1,
                    'allowed_roles': ['admin', 'doctor', 'receptionist']
                },
                {
                    'name': 'patients',
                    'display_name': 'Pacientes',
                    'description': 'Gestión de pacientes y expedientes',
                    'icon': 'fas fa-users',
                    'url_name': 'patients:list',
                    'category': 'core',
                    'order': 2,
                    'allowed_roles': ['admin', 'doctor', 'receptionist']
                },
                {
                    'name': 'appointments',
                    'display_name': 'Citas',
                    'description': 'Calendario y gestión de citas médicas',
                    'icon': 'fas fa-calendar-alt',
                    'url_name': 'appointments:calendar',
                    'category': 'core',
                    'order': 3,
                    'allowed_roles': ['admin', 'doctor', 'receptionist']
                },
                {
                    'name': 'medical_records',
                    'display_name': 'Expedientes',
                    'description': 'Historia clínica y registros médicos',
                    'icon': 'fas fa-file-medical',
                    'url_name': 'medical_records:index',
                    'category': 'core',
                    'order': 4,
                    'requires_medical_license': True,
                    'allowed_roles': ['admin', 'doctor']
                },
            ]

            # Medical specialty modules (MEDIUM and ADVANCED plans)
            specialty_modules = [
                {
                    'name': 'cardiology',
                    'display_name': 'Cardiología',
                    'description': 'Especialidad en enfermedades del corazón',
                    'icon': 'fas fa-heartbeat',
                    'url_name': '',
                    'category': 'medical',
                    'min_plan_required': 'MEDIUM',
                    'order': 1,
                    'requires_medical_license': True,
                    'allowed_roles': ['admin', 'doctor']
                },
                {
                    'name': 'pediatrics',
                    'display_name': 'Pediatría',
                    'description': 'Atención médica de niños y adolescentes',
                    'icon': 'fas fa-baby',
                    'url_name': '',
                    'category': 'medical',
                    'min_plan_required': 'MEDIUM',
                    'order': 2,
                    'requires_medical_license': True,
                    'allowed_roles': ['admin', 'doctor']
                },
                {
                    'name': 'gynecology',
                    'display_name': 'Ginecología',
                    'description': 'Salud reproductiva femenina',
                    'icon': 'fas fa-female',
                    'url_name': '',
                    'category': 'medical',
                    'min_plan_required': 'MEDIUM',
                    'order': 3,
                    'requires_medical_license': True,
                    'allowed_roles': ['admin', 'doctor']
                },
                {
                    'name': 'dermatology',
                    'display_name': 'Dermatología',
                    'description': 'Enfermedades de la piel',
                    'icon': 'fas fa-user-md',
                    'url_name': '',
                    'category': 'medical',
                    'min_plan_required': 'ADVANCED',
                    'order': 4,
                    'requires_medical_license': True,
                    'allowed_roles': ['admin', 'doctor']
                },
                {
                    'name': 'nutrition',
                    'display_name': 'Nutrición',
                    'description': 'Evaluación y planes nutricionales',
                    'icon': 'fas fa-leaf',
                    'url_name': 'nutrition:dashboard',
                    'category': 'medical',
                    'min_plan_required': 'MEDIUM',
                    'order': 5,
                    'requires_medical_license': True,
                    'allowed_roles': ['admin', 'doctor']
                },
                {
                    'name': 'psychology',
                    'display_name': 'Psicología',
                    'description': 'Evaluaciones y terapias psicológicas',
                    'icon': 'fas fa-brain',
                    'url_name': 'psychology:dashboard',
                    'category': 'medical',
                    'min_plan_required': 'MEDIUM',
                    'order': 6,
                    'requires_medical_license': True,
                    'allowed_roles': ['admin', 'doctor']
                },
            ]

            # Administrative modules
            admin_modules = [
                {
                    'name': 'billing',
                    'display_name': 'Facturación',
                    'description': 'Gestión de facturación y pagos',
                    'icon': 'fas fa-file-invoice-dollar',
                    'url_name': '',
                    'category': 'admin',
                    'min_plan_required': 'MEDIUM',
                    'order': 1,
                    'allowed_roles': ['admin', 'receptionist']
                },
                {
                    'name': 'equipment',
                    'display_name': 'Equipos',
                    'description': 'Inventario y mantenimiento de equipos',
                    'icon': 'fas fa-tools',
                    'url_name': '',
                    'category': 'admin', 
                    'min_plan_required': 'MEDIUM',
                    'order': 2,
                    'allowed_roles': ['admin', 'receptionist']
                },
                {
                    'name': 'accounts',
                    'display_name': 'Usuarios',
                    'description': 'Gestión de usuarios y permisos',
                    'icon': 'fas fa-user-cog',
                    'url_name': '',
                    'category': 'admin',
                    'order': 3,
                    'allowed_roles': ['admin']
                },
            ]

            # Reports and analytics modules
            reports_modules = [
                {
                    'name': 'reports_basic',
                    'display_name': 'Reportes Básicos',
                    'description': 'Reportes estándar del sistema',
                    'icon': 'fas fa-chart-bar',
                    'url_name': '',
                    'category': 'reports',
                    'order': 1,
                    'allowed_roles': ['admin', 'doctor']
                },
                {
                    'name': 'reports_advanced',
                    'display_name': 'Analytics Avanzado',
                    'description': 'Dashboards ejecutivos y KPIs',
                    'icon': 'fas fa-chart-line',
                    'url_name': '',
                    'category': 'reports',
                    'min_plan_required': 'MEDIUM',
                    'order': 2,
                    'allowed_roles': ['admin']
                },
                {
                    'name': 'business_intelligence',
                    'display_name': 'Business Intelligence',
                    'description': 'Análisis predictivo y tendencias',
                    'icon': 'fas fa-brain',
                    'url_name': '',
                    'category': 'reports',
                    'min_plan_required': 'ADVANCED',
                    'order': 3,
                    'allowed_roles': ['admin']
                },
            ]

            # Communication modules
            communication_modules = [
                {
                    'name': 'notifications',
                    'display_name': 'Notificaciones',
                    'description': 'Centro de notificaciones del sistema',
                    'icon': 'fas fa-bell',
                    'url_name': '',
                    'category': 'communication',
                    'order': 1,
                    'allowed_roles': ['admin', 'doctor', 'receptionist']
                },
                {
                    'name': 'telemedicine',
                    'display_name': 'Telemedicina',
                    'description': 'Consultas médicas virtuales',
                    'icon': 'fas fa-video',
                    'url_name': '',
                    'category': 'communication',
                    'min_plan_required': 'MEDIUM',
                    'order': 2,
                    'requires_medical_license': True,
                    'allowed_roles': ['admin', 'doctor']
                },
                {
                    'name': 'patient_portal',
                    'display_name': 'Portal del Paciente',
                    'description': 'Acceso para pacientes en línea',
                    'icon': 'fas fa-user-shield',
                    'url_name': '',
                    'category': 'communication',
                    'min_plan_required': 'ADVANCED',
                    'order': 3,
                    'allowed_roles': ['admin', 'patient']
                },
            ]

            # Integration modules
            integration_modules = [
                {
                    'name': 'api_access',
                    'display_name': 'API Externa',
                    'description': 'Integraciones con sistemas externos',
                    'icon': 'fas fa-plug',
                    'url_name': '',
                    'category': 'integration',
                    'min_plan_required': 'ADVANCED',
                    'order': 1,
                    'allowed_roles': ['admin']
                },
                {
                    'name': 'laboratory_integration',
                    'display_name': 'Laboratorios',
                    'description': 'Integración con laboratorios externos',
                    'icon': 'fas fa-flask',
                    'url_name': '',
                    'category': 'integration',
                    'min_plan_required': 'ADVANCED',
                    'order': 2,
                    'allowed_roles': ['admin', 'doctor']
                },
            ]

            # Combine all modules
            all_modules = (core_modules + specialty_modules + admin_modules + 
                          reports_modules + communication_modules + integration_modules)

            created_count = 0
            updated_count = 0

            # First, create/update all parent modules
            for module_data in all_modules:
                module, created = SystemModule.objects.update_or_create(
                    name=module_data['name'],
                    defaults=module_data
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'[+] Creado: {module.display_name}')
                else:
                    updated_count += 1
                    self.stdout.write(f'[*] Actualizado: {module.display_name}')

            # Create submodules for specialty modules
            self.create_specialty_submodules(created_count, updated_count)

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nInicialización completada:\n'
                    f'- {created_count} módulos creados\n'
                    f'- {updated_count} módulos actualizados\n'
                    f'- {len(all_modules)} módulos totales'
                )
            )

    def create_specialty_submodules(self, created_count, updated_count):
        """Create submodules for specialty modules"""
        
        # Get parent modules
        nutrition_module = SystemModule.objects.get(name='nutrition')
        psychology_module = SystemModule.objects.get(name='psychology')
        
        # Nutrition submodules
        nutrition_submodules = [
            {
                'name': 'nutrition_dashboard',
                'display_name': 'Dashboard',
                'description': 'Panel principal de nutrición',
                'icon': 'fas fa-tachometer-alt',
                'url_name': 'nutrition:dashboard',
                'category': 'medical',
                'parent_module': nutrition_module,
                'order': 1,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
            {
                'name': 'nutrition_assessments',
                'display_name': 'Evaluaciones',
                'description': 'Evaluaciones nutricionales',
                'icon': 'fas fa-clipboard-check',
                'url_name': 'nutrition:assessment_list',
                'category': 'medical',
                'parent_module': nutrition_module,
                'order': 2,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
            {
                'name': 'nutrition_diet_plans',
                'display_name': 'Planes Dietéticos',
                'description': 'Planes y menús dietéticos',
                'icon': 'fas fa-utensils',
                'url_name': 'nutrition:diet_plan_list',
                'category': 'medical',
                'parent_module': nutrition_module,
                'order': 3,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
            {
                'name': 'nutrition_consultations',
                'display_name': 'Consultas',
                'description': 'Consultas nutricionales',
                'icon': 'fas fa-stethoscope',
                'url_name': 'nutrition:consultation_list',
                'category': 'medical',
                'parent_module': nutrition_module,
                'order': 4,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
            {
                'name': 'nutrition_goals',
                'display_name': 'Metas',
                'description': 'Objetivos nutricionales',
                'icon': 'fas fa-bullseye',
                'url_name': 'nutrition:goals_list',
                'category': 'medical',
                'parent_module': nutrition_module,
                'order': 5,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
        ]
        
        # Psychology submodules
        psychology_submodules = [
            {
                'name': 'psychology_dashboard',
                'display_name': 'Dashboard',
                'description': 'Panel principal de psicología',
                'icon': 'fas fa-tachometer-alt',
                'url_name': 'psychology:dashboard',
                'category': 'medical',
                'parent_module': psychology_module,
                'order': 1,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
            {
                'name': 'psychology_evaluations',
                'display_name': 'Evaluaciones',
                'description': 'Evaluaciones psicológicas',
                'icon': 'fas fa-clipboard-list',
                'url_name': 'psychology:evaluation_list',
                'category': 'medical',
                'parent_module': psychology_module,
                'order': 2,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
            {
                'name': 'psychology_sessions',
                'display_name': 'Sesiones de Terapia',
                'description': 'Sesiones de terapia psicológica',
                'icon': 'fas fa-calendar-check',
                'url_name': 'psychology:session_list',
                'category': 'medical',
                'parent_module': psychology_module,
                'order': 3,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
            {
                'name': 'psychology_treatment_plans',
                'display_name': 'Planes de Tratamiento',
                'description': 'Planes de tratamiento psicológico',
                'icon': 'fas fa-map',
                'url_name': 'psychology:treatment_plan_list',
                'category': 'medical',
                'parent_module': psychology_module,
                'order': 4,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
            {
                'name': 'psychology_goals',
                'display_name': 'Objetivos',
                'description': 'Objetivos psicológicos',
                'icon': 'fas fa-bullseye',
                'url_name': 'psychology:goal_list',
                'category': 'medical',
                'parent_module': psychology_module,
                'order': 5,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
            {
                'name': 'psychology_tests',
                'display_name': 'Tests Psicológicos',
                'description': 'Catálogo de tests psicológicos',
                'icon': 'fas fa-brain',
                'url_name': 'psychology:test_list',
                'category': 'medical',
                'parent_module': psychology_module,
                'order': 6,
                'min_plan_required': 'MEDIUM',
                'allowed_roles': ['admin', 'doctor']
            },
        ]
        
        # Create/update all submodules
        all_submodules = nutrition_submodules + psychology_submodules
        
        for submodule_data in all_submodules:
            submodule, created = SystemModule.objects.update_or_create(
                name=submodule_data['name'],
                defaults=submodule_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'[+] Submódulo creado: {submodule.display_name}')
            else:
                updated_count += 1
                self.stdout.write(f'[*] Submódulo actualizado: {submodule.display_name}')