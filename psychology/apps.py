from django.apps import AppConfig


class PsychologyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'psychology'
    verbose_name = 'Psicología'
    
    def ready(self):
        """
        Configuración inicial cuando la aplicación está lista
        """
        try:
            import psychology.signals
        except ImportError:
            pass
