from django.core.management.base import BaseCommand, CommandError
from aristotle_mdr.utils.utils import fetch_aristotle_settings


class Command(BaseCommand):
    help = 'Validates that Aristotle settings are correct'

    def handle(self, *args, **options):
        try:
            fetch_aristotle_settings()
            self.stdout.write('Aristotle Settings are valid! :)')
        except:
            raise
