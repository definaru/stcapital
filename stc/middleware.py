from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin


class DeviceInfoMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        user_agent = request.META.get('HTTP_USER_AGENT')
        if not user_agent:
            return HttpResponseForbidden("Access denied: No User-Agent detected.")

        if request.user.is_authenticated:
            request.session['device_info'] = user_agent
            print(f"Device Info Middleware: {request.session['device_info']}")

    def process_response(self, request, response):
        return response