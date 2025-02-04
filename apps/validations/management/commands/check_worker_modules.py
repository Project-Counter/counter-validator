import logging
import sys

import requests
from django.conf import settings
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Checks that validation modules set up in settings are running"

    def handle(self, *args, **options):
        worker_url = settings.CTOOLS_URL
        logger.info(f"Worker URL: {worker_url}")
        try:
            response = requests.get(worker_url)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error connecting to worker: {e}")
            sys.exit(1)
        logger.info("Worker is running")
        logger.info("Data: %s", response.json())
        sys.exit(0)
