from django import forms
from django.conf import settings
from django_altcha import AltchaField


class DAMForm(forms.Form):
    """Form containing Altcha field for proof-of-work.

    See django_altcha.AltchaField for more supported options.
    """

    captcha = AltchaField(
        maxnumber=getattr(settings, 'ALTCHA_MAX_NUMBER', 1000000),
        # floating='bottom',   # Enables floating behavior
        debug='true',      # Enables debug mode (for development)
        hidefooter='true',
        auto='onload',
    )
