"""
Commande personnalisée pour créer le superadmin SolidariCash.
Usage: python manage.py create_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée le compte administrateur SolidariCash par défaut'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Nom utilisateur admin')
        parser.add_argument('--password', default='Admin@SolidariCash2025', help='Mot de passe admin')
        parser.add_argument('--email', default='admin@solidaricash.com', help='Email admin')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"L'utilisateur '{username}' existe déjà."))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Super',
            last_name='Admin',
            role=User.ROLE_ADMIN,
        )
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Administrateur créé avec succès !\n"
            f"  Username : {username}\n"
            f"  Password : {password}\n"
            f"  Email    : {email}\n"
            f"\n⚠ Changez le mot de passe en production !"
        ))
