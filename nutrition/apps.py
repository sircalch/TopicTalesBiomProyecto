from django.apps import AppConfig


class NutritionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nutrition'
    verbose_name = 'Módulo de Nutrición'
    
    def ready(self):
        """
        Importar señales cuando la aplicación esté lista
        """
        try:
            import nutrition.signals
        except ImportError:
            pass
