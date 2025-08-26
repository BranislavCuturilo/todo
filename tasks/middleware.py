from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class DisableCSRFMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Disable CSRF for login and register
        if request.path in ['/login/', '/register/', '/admin/login/']:
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
