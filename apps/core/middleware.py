from time import sleep

from django.conf import settings


class DebugSleepMiddleware:
    """
    Simple middleware to simulate slow responses - it adds a delay to every request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        sleep(settings.DEBUG_SLEEP)
        return response
