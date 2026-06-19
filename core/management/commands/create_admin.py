from django.core.management.base import BaseCommand
from core.models import Utilisateur

class Command(BaseCommand):
    help = 'Crée un superutilisateur admin s\'il n\'existe pas déjà'

    def handle(self, *args, **kwargs):
        if not Utilisateur.objects.filter(username='admin').exists():
            Utilisateur.objects.create_superuser(
                username='admin',
                email='admin@gestcli.cm',
                password='Admin1234',
                first_name='Dylane',
                last_name='Deutcha',
                role='admin',
            )
            self.stdout.write(self.style.SUCCESS('Superutilisateur admin créé avec succès'))
        else:
            self.stdout.write(self.style.WARNING('Le superutilisateur admin existe déjà'))