from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    # def process_view(self, request, view_func, view_args, view_kwargs):
    #     # Daftar path yang memerlukan login
    #     login_required_paths = [
    #         '/topics/', 
    #         '/role/', 
    #         '/courses/', 
    #         '/profile/', 
    #         '/access_course/'
    #     ]

        if request.path in login_required_paths and not request.user.is_authenticated:
            return redirect(reverse('login') + '?next=' + request.path)

        return None
