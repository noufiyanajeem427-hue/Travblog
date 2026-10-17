from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be logged in to access certain pages.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_urls = [reverse('login'), reverse('index')]  # Move inside the method

        if not request.session.get('userid') and not any(request.path.startswith(url) for url in exempt_urls):
            return redirect('login')  # Redirect unauthorized users

        return self.get_response(request)
