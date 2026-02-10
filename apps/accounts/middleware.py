from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch


class RedirectAuthenticatedUserMiddleware:
    """
    Redirect authenticated users away from auth pages.
    Safe for Render + DEBUG=False.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                auth_paths = {
                    reverse("doctor_login"),
                    reverse("patient_login"),
                }

                if request.path in auth_paths:
                    # Redirect based on role later if needed
                    return redirect("home")

            except NoReverseMatch:
                pass  # Never crash middleware

        return self.get_response(request)
