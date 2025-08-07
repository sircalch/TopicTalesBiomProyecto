from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Organization, UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix user profile associations'

    def handle(self, *args, **options):
        users = User.objects.all()
        
        for user in users:
            try:
                profile = user.profile
                self.stdout.write(f'Usuario {user.username} ya tiene perfil con org: {profile.organization.name}')
            except UserProfile.DoesNotExist:
                # Usuario sin perfil, crear uno
                org = Organization.objects.filter(subscription__plan__in=['MEDIUM', 'ADVANCED']).first()
                if org:
                    profile = UserProfile.objects.create(
                        user=user,
                        organization=org
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'Perfil creado para {user.username} con organización {org.name} (Plan: {org.subscription.plan})')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'No se encontró organización con plan MEDIUM/ADVANCED para {user.username}')
                    )
        
        self.stdout.write(self.style.SUCCESS('Proceso completado'))