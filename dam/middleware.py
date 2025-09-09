import ipaddress
import re
import time
from urllib.parse import quote_plus

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
        self.excluded_paths = getattr(settings,
                                      'ALTCHA_EXCLUDE_PATHS',
                                      set())
        ip_exclusions = getattr(settings,
                                'ALTCHA_EXCLUDE_IPS',
                                [])
        self.excluded_ips = make_ip_list(ip_exclusions)
        self.excluded_ips.sort()
        header_exclusions = getattr(settings,
                                    'ALTCHA_EXCLUDE_HEADERS',
                                    {})
        self.excluded_headers = make_excluded_headers(header_exclusions)

    def exclude_ip(self, request):
        """Determine if client IP can skip Altcha verification.

        X-Forwarded-For header may include chain of IPs, if so, use first
        address.
        """
        if not self.excluded_ips:
            # There are no excluded IP addresses.
            return False
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR',
                                     request.META.get('REMOTE_ADDR')).split(',')[0]
        try:
            client_ip = ipaddress.ip_address(client_ip)
        except ValueError:
            # Client IP address not valid.
            return False
        for network in self.excluded_ips:
            if client_ip < network[0]:
                # Networks are sorted, so if client_ip is less than the
                # current networks first address, client_ip is not in the list.
                break
            if client_ip in network:
                return True
        return False

    def exclude_headers(self, request):
        """Determine if request headers warrant skipping verification."""
        for header, pattern in self.excluded_headers.items():
            value = request.headers.get(header, '')
            if value.strip() and pattern.search(value):
                # Client sent header that allows bypassing verification.
                return True
        return False

    def process_request(self, request):
        if time.time() <= request.session.get(self.altcha_session_key, 0):
            # User already passed Altcha verification and their approval hasn't expired yet.
            return None
        elif request.path in {reverse('dam:challenge')} | set(self.excluded_paths):
            # Path is exempt from Altcha verification.
            return None
        elif self.exclude_ip(request):
            # IP address is exempt from Altcha verification.
            return None
        elif self.exclude_headers(request):
            # Request includes HTTP header with value exempt from verification.
            return None
        # Redirect to Altcha verification page
        dam_url = f'{reverse("dam:challenge")}?next={quote_plus(request.get_full_path())}'
        request.session[f'referer{request.get_full_path()}'] = request.META.get('HTTP_REFERER', '')
        return redirect(dam_url)


def make_ip_list(ip_addresses):
    """Convert supplied [CIDR] IP addresses to ip address objects.

    Takes an iterable of individual or CIDR IP addresses, and converts
    them to a list of ipaddress.ip_network objects.
    """
    networks = set()
    for address in ip_addresses:
        try:
            networks.add(ipaddress.ip_network(address))
        except ValueError as err:
            # Skip invalid ip address
            print('Could not exclude supplied ip address', err)
    return list(networks)


def make_excluded_headers(header_exclusions):
    """Convert headers' string values into case-insensitive regular expression patterns."""
    return {k: re.compile(v, re.I) for k, v in header_exclusions.items()}
