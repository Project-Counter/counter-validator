from django.conf import settings
from django_celery_results.models import TaskResult
from redis import Redis


def get_validation_queue_length():
    redis = Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_CELERY_DB_NUMBER
    )
    return redis.llen(settings.CELERY_VALIDATION_QUEUE)


def get_number_of_running_validations():
    return TaskResult.objects.filter(status="STARTED").count()
