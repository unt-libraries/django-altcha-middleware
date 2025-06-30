import json
import time
import datetime
from base64 import b64decode
from urllib.parse import quote_plus

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.cache import cache
from altcha import create_challenge, verify_solution, solve_challenge

from .forms import DAMForm
from .decorators import altcha_verify


def dam_challenge(request):
    """Make the user solve an Altcha challenge before allowing access."""
    # For POST requests, check the challenge response and see if it validates
    if request.method == 'POST':
        try:
            payload = json.loads(b64decode(request.POST.get('altcha')))
        except Exception:
            payload = {}
        ok, err = verify_solution(payload, settings.ALTCHA_HMAC_KEY, check_expires=True)
        destination = request.POST.get('next', ['/'])
        # If the solution validates and hasn't already been seen, create/update their session dam
        # expiration and send them off, as well as saving the challenge in cache.
        if isinstance(payload, dict) and ok and destination and not cache.get(payload.challenge):
            expire_mins = getattr(settings, 'ALTCHA_EXPIRE_MINUTES', 60)
            cache.set(
                payload.challenge,
                't',
                timeout=expire_mins*60)
            altcha_session_key = getattr(settings, 'ALTCHA_SESSION_KEY', 'altcha_verified')
            request.session[altcha_session_key] = time.time() + expire_mins*60
            return redirect(destination)
        # Otherwise, reject them.
        else:
            return HttpResponse('Challenge failed or no longer valid.', status=429)
    # For normal requests, create the challenge and send it.
    else:
        challenge = create_challenge(
            expires=datetime.datetime.now() + datetime.timedelta(seconds=30),
            max_number=settings.ALTCHA_MAX_NUMBER,
            hmac_key=settings.ALTCHA_HMAC_KEY,
            # Use the params to add arbitrary values to the salt, potentially increasing security
            params={},
        )
        return render(
            request,
            'dam_challenge.html',
            {'challenge': challenge,
             'js_src_url': getattr(settings, 'ALTCHA_JS_URL', '/static/altcha/altcha.min.js')
             'next_url': request.GET.get('next', '/')}
        )


@altcha_verify
def hello(request):
    return HttpResponse('hello there')
