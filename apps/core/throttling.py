from rest_framework.throttling import SimpleRateThrottle


class APIKeyBasedThrottle(SimpleRateThrottle):
    scope = "api_keys"

    def get_cache_key(self, request, view):
        """
        Returns the user ID, but only for requests using API keys.
        This leads to rate limiting on user-level, but only for requests using API keys.
        Thus, different API keys for the same user will be throttled together.
        """
        if request.headers.get("Authorization") and request.user and request.user.is_authenticated:
            return str(request.user.id)
        return None
