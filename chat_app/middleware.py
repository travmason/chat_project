# chat_app/middleware.py
from django.contrib.auth import login, get_user_model

class AutoLoginAsGuestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.guest_user = None  # Cache the guest user instance

    def __call__(self, request):
        if request.path.startswith('/demo/'):  # Apply only to demo URLs
            if not request.user.is_authenticated:
                if self.guest_user is None:
                    User = get_user_model()
                    self.guest_user = User.objects.get(username='guest')
                login(request, self.guest_user)
        response = self.get_response(request)
        return response