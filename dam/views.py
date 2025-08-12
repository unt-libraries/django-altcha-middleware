import json
import time
import datetime
from base64 import b64decode


from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.cache import cache
from altcha import create_challenge, verify_solution


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
        if (isinstance(payload, dict) and ok and destination
                and not cache.get(payload.get('challenge'))):
            challenge_expire_mins = getattr(settings, 'ALTCHA_CHALLENGE_EXPIRE_MINUTES', 2)
            auth_expire_mins = getattr(settings, 'ALTCHA_AUTH_EXPIRE_MINUTES', 480)
            cache.set(
                payload['challenge'],
                't',
                timeout=challenge_expire_mins*60)
            altcha_session_key = getattr(settings, 'ALTCHA_SESSION_KEY', 'altcha_verified')
            request.session[altcha_session_key] = time.time() + auth_expire_mins*60
            return redirect(destination)
        # Otherwise, reject them.
        return HttpResponse('Challenge failed or no longer valid.', status=400)
    # For normal requests, create the challenge and send it.
    else:
        challenge_expire_mins = getattr(settings, 'ALTCHA_CHALLENGE_EXPIRE_MINUTES', 2)
        challenge = create_challenge(
            expires=datetime.datetime.now() + datetime.timedelta(minutes=challenge_expire_mins),
            max_number=settings.ALTCHA_MAX_NUMBER,
            hmac_key=settings.ALTCHA_HMAC_KEY,
            # Use the params to add arbitrary values to the salt, potentially increasing security
            params=getattr(settings, 'ALTCHA_SALT_PARAMS', {}),
        )
        return render(
            request,
            'dam_challenge.html',
            {'challenge': challenge,
             'js_src_url': getattr(settings, 'ALTCHA_JS_URL', '/static/altcha/altcha.min.js'),
             'next_url': request.GET.get('next', '/')}
        )
