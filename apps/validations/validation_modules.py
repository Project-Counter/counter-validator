"""
There may be more than one validation module available. We want to distribute the load between them.
To do this, we primarily rely on using only as many celery workers for the `validation` queue
as there are validation modules available. But to protect against the case of incorrect celery
setup or other issues, we also implement a locking mechanism to ensure that only one validation
task is running on a validation module at a time.

This module contains functions to manage the locking mechanism.
"""

from django.conf import settings
from redis import Redis
from redis.lock import Lock

vm_lock_prefix = "vm_lock_"


def get_locking_redis() -> Redis:
    return Redis.from_url(settings.REDIS_URL)


def lock_name(vm_url: str) -> str:
    return f"{vm_lock_prefix}{vm_url}"


def is_validation_module_locked(vm_url: str, redis: Redis) -> bool:
    lock = Lock(redis, lock_name(vm_url), timeout=settings.VALIDATION_MODULE_LOCK_TIMEOUT)
    return lock.locked()


def get_available_validation_module_url() -> str | None:
    redis = get_locking_redis()
    for vm_url in settings.VALIDATION_MODULES_URLS:
        if not is_validation_module_locked(vm_url, redis):
            return vm_url


def create_validation_module_lock(vm_url: str) -> Lock:
    redis = get_locking_redis()
    lock = Lock(redis, lock_name(vm_url))
    return lock
