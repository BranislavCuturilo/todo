from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key


class Command(BaseCommand):
    help = 'Generate a secure SECRET_KEY for production'

    def handle(self, *args, **options):
        secret_key = get_random_secret_key()
        self.stdout.write(
            self.style.SUCCESS(f'Generated SECRET_KEY: {secret_key}')
        )
        self.stdout.write(
            self.style.WARNING(
                'Copy this key to your .env file as SECRET_KEY=your-key-here'
            )
        )



