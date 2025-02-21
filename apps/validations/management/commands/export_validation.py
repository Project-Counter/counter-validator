import logging
from pathlib import Path

from django.core.management import BaseCommand

from validations.export import ValidationXlsxExporter
from validations.models import Validation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Exports one validation identified by its ID"

    def add_arguments(self, parser):
        parser.add_argument("id", type=str)
        parser.add_argument("outfile", type=str)

    def handle(self, *args, **options):
        val = Validation.objects.get(pk=options["id"])
        exporter = ValidationXlsxExporter(val)
        with Path(options["outfile"]).open("wb") as f:
            f.write(exporter.export())
