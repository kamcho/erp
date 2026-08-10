import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)

class GlobalErrorHandlingMiddleware:
    """
    Middleware to catch all unhandled exceptions and render a friendly error page,
    ensuring the user is always informed that the issue is being fixed.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            # Keep intentional access-denied pages (and other auth challenges) as-is
            if response.status_code in (401, 403):
                return response
            if response.status_code >= 400:
                context = {
                    'status_code': response.status_code,
                    'is_404': response.status_code == 404,
                    'is_403': response.status_code == 403,
                    'path': request.path,
                }
                return render(request, 'core/error.html', context, status=response.status_code)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception caught by middleware: {e}", exc_info=True)
            context = {
                'status_code': 500,
                'error_message': str(e),
                'path': request.path,
            }
            return render(request, 'core/error.html', context, status=500)

    def process_exception(self, request, exception):
        from django.core.exceptions import PermissionDenied
        if isinstance(exception, PermissionDenied):
            return render(
                request,
                'core/error.html',
                {
                    'status_code': 403,
                    'is_403': True,
                    'is_404': False,
                    'error_message': str(exception) or 'You do not have permission to access this page.',
                    'path': request.path,
                },
                status=403,
            )
        logger.error(f"process_exception caught: {exception}", exc_info=True)
        context = {
            'status_code': 500,
            'error_message': str(exception),
            'path': request.path,
        }
        return render(request, 'core/error.html', context, status=500)
