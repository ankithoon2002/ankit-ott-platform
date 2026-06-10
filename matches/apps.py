from django.apps import AppConfig
import os

class MatchesConfig(AppConfig):
    name = 'matches'

    def ready(self):
        # Run superuser creation script
        try:
            from create_admin import create_superuser
            create_superuser()
        except Exception as e:
            print(f"Error running create_superuser: {e}")
