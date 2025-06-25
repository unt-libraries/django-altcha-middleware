from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class AltchaMiddleware(MiddlewareMixin):
    """Prompt user to complete Altcha proof-of-work if needed."""

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.altcha_session_key = getattr(settings,
                                          'ALTCHA_SESSION_KEY',
                                          'altcha_verified')
        self.exclude_paths = getattr(settings,
                                     'ALTCHA_EXCLUDE_PATHS',
                                     set())
        self.exclude_ips = getattr(settings,
                                   'ALTCHA_EXCLUDE_IPS',
                                   set())

    def process_request(self, request):
        if request.session.get(self.altcha_session_key, False):
            # User already passed Altcha verification
            return None
        elif request.path in {reverse('dam:dam_form')} | set(self.exclude_paths):
            # Path is exempt from Altcha verification
            return None
        # TODO add ip whitelisting
        # Redirect to Altcha verification page
        dam_url = f'{reverse("dam:dam_form")}?next={request.path}'
        return redirect(dam_url)
