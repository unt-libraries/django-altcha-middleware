from django.utils.decorators import decorator_from_middleware

from .middleware import AltchaMiddleware


# Use the altcha_verify decorator on your app's views to require Altcha
# verification on specific views, rather than all requests
altcha_verify = decorator_from_middleware(AltchaMiddleware)
