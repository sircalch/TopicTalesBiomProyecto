from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, Organization, Subscription, UserProfile, SystemModule, ModulePermission


class Command(BaseCommand):
    help = 'Create sample data for testing the dynamic module system'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Creando datos de ejemplo...')
            
            # Create sample organization
            organization, created = Organization.objects.get_or_create(
                name='Clínica Ejemplo TopicTales',
                defaults={
                    'legal_name': 'Clínica Ejemplo TopicTales S.A. de C.V.',
                    'tax_id': 'EJE123456789',
                    'address': 'Av. Revolución 123, Ciudad de México',
                    'phone': '+52 55 1234 5678',
                    'email': 'contacto@clinicaejemplo.com',
                    'director_name': 'Dr. Juan Pérez López',
                    'director_license': '123456789'
                }
            )
            
            if created:
                self.stdout.write('[+] Organización creada: Clínica Ejemplo TopicTales')
            
            # Create subscription (MEDIUM plan for testing)
            subscription, created = Subscription.objects.get_or_create(
                organization=organization,
                defaults={
                    'plan': 'MEDIUM',
                    'status': 'active',
                    'start_date': timezone.now(),
                    'end_date': timezone.now() + timedelta(days=365),
                    'max_patients': 500,
                    'max_users': 10,
                    'current_patients': 25,
                    'current_users': 3,
                    'monthly_price': 2500.00,
                    'currency': 'MXN'
                }
            )
            
            if created:
                self.stdout.write('[+] Suscripción creada: Plan Medio')
            
            # Create sample users
            users_data = [
                {
                    'username': 'admin',
                    'email': 'admin@clinicaejemplo.com',
                    'first_name': 'Administrador',
                    'last_name': 'Sistema',
                    'role': 'admin',
                    'password': 'admin123'
                },
                {
                    'username': 'dr.martinez',
                    'email': 'dr.martinez@clinicaejemplo.com',
                    'first_name': 'Carlos',
                    'last_name': 'Martínez García',
                    'role': 'doctor',
                    'password': 'doctor123',
                    'specialty': 'Medicina General',
                    'professional_license': '987654321'
                },
                {
                    'username': 'recepcion',
                    'email': 'recepcion@clinicaejemplo.com',
                    'first_name': 'María',
                    'last_name': 'González López',
                    'role': 'receptionist',
                    'password': 'recep123'
                }
            ]
            
            created_users = []
            for user_data in users_data:
                password = user_data.pop('password')
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults=user_data
                )
                
                if created:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(f'[+] Usuario creado: {user.username}')
                    
                    # Create user profile
                    UserProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'organization': organization,
                            'department': 'Medicina General' if user.role == 'doctor' else 'Administración',
                            'position': user.get_role_display(),
                            'hire_date': timezone.now().date(),
                            'language': 'es',
                            'timezone': 'America/Mexico_City'
                        }
                    )
                    
                created_users.append(user)
            
            # Create module permissions for the organization
            # Enable all modules that should be available for MEDIUM plan
            modules_to_enable = [
                'dashboard', 'patients', 'appointments', 'medical_records',
                'cardiology', 'pediatrics', 'gynecology', 
                'billing', 'equipment', 'accounts',
                'reports_basic', 'reports_advanced',
                'notifications', 'telemedicine'
            ]
            
            enabled_count = 0
            for module_name in modules_to_enable:
                try:
                    module = SystemModule.objects.get(name=module_name)
                    permission, created = ModulePermission.objects.get_or_create(
                        organization=organization,
                        module=module,
                        defaults={
                            'is_enabled': True,
                            'custom_settings': {}
                        }
                    )
                    
                    if created:
                        enabled_count += 1
                        self.stdout.write(f'[+] Módulo habilitado: {module.display_name}')
                        
                except SystemModule.DoesNotExist:
                    self.stdout.write(f'[-] Módulo no encontrado: {module_name}')
            
            # Disable advanced modules for MEDIUM plan
            advanced_modules = [
                'dermatology', 'nutrition', 'psychology',
                'business_intelligence', 'patient_portal',
                'api_access', 'laboratory_integration'
            ]
            
            for module_name in advanced_modules:
                try:
                    module = SystemModule.objects.get(name=module_name)
                    permission, created = ModulePermission.objects.get_or_create(
                        organization=organization,
                        module=module,
                        defaults={
                            'is_enabled': False,
                            'custom_settings': {'upgrade_required': True}
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'[*] Módulo deshabilitado (requiere upgrade): {module.display_name}')
                        
                except SystemModule.DoesNotExist:
                    pass
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nDatos de ejemplo creados exitosamente:\n'
                    f'- 1 organización: {organization.name}\n'
                    f'- 1 suscripción: {subscription.get_plan_display()}\n'
                    f'- {len(created_users)} usuarios creados\n'
                    f'- {enabled_count} módulos habilitados\n\n'
                    f'Credenciales de acceso:\n'
                    f'Admin: admin / admin123\n'
                    f'Doctor: dr.martinez / doctor123\n'
                    f'Recepción: recepcion / recep123'
                )
            )