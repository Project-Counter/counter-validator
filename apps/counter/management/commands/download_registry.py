from core.tasks import update_registry_models
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Download data containing counter registry info"

    def handle(self, *args, **options):
        update_registry_models()
