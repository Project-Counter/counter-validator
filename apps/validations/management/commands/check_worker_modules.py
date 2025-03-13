import logging
import sys
from collections import Counter

import requests
from django.conf import settings
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Checks that validation modules set up in settings are running"

    def handle(self, *args, **options):
        stats = Counter()
        for worker_url in settings.VALIDATION_MODULES_URLS:
            logger.info(f"Worker URL: {worker_url}")
            try:
                response = requests.get(worker_url)
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"  Error connecting to worker: {e}")
                stats["error"] += 1
            else:
                logger.info("  Worker is running")
                logger.info("  Data: %s", response.json())
                stats["ok"] += 1
        logger.info("Summary: %s", stats)
        sys.exit(stats["error"] and 1)
