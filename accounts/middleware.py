"""
TopicTales Biomédica - Custom Middleware
"""
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class DisableCacheMiddleware(MiddlewareMixin):
    """
    Middleware to disable browser caching in development mode
    """
    def process_response(self, request, response):
        if settings.DEBUG:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response