from django.apps import AppConfig

class GamificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gamification'

    def ready(self):
        # Isso ativa os signals quando o Django inicia
        import apps.gamification.signals