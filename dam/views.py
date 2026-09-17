import json
import time
import datetime
import secrets


from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.core.cache import cache
from django.views.decorators.http import require_GET, require_POST
from altcha import create_challenge, verify_solution, Payload

from dam.middleware import get_client_ip


@require_GET
def dam_challenge(request):
    """Provide user an Altcha challenge to solve before allowing access."""
    challenge_expire_mins = getattr(settings, 'ALTCHA_CHALLENGE_EXPIRE_MINUTES', 2)
    counter = secrets.randbelow(settings.ALTCHA_COST) + settings.ALTCHA_COST
    challenge = create_challenge(
        algorithm='PBKDF2/SHA-256',
        cost=settings.ALTCHA_COST,
        counter=counter,
        expires_at=datetime.datetime.now() + datetime.timedelta(minutes=challenge_expire_mins),
        hmac_secret=settings.ALTCHA_HMAC_KEY,
        hmac_key_secret=settings.ALTCHA_HMAC_KEY_SECRET,
    )
    next_url = request.GET.get('next', '/')
    return render(
        request,
        'dam_challenge.html',
        {
            'challenge': json.dumps(challenge.to_dict()),
            'site_icon_url': getattr(settings, 'ALTCHA_SITE_ICON_URL', ''),
            'js_src_url': getattr(
                settings, 'ALTCHA_JS_URL', f'{settings.STATIC_URL}altcha/altcha.min.js'),
            'css_src_url': getattr(
                settings, 'ALTCHA_CSS_URL', f'{settings.STATIC_URL}dam/dam.css'),
            'altcha_message': getattr(settings,
                                      'ALTCHA_MESSAGE',
                                      'Gauging your humanity...This may take some seconds.'),
            'next_url': next_url,
            'help_text': getattr(settings,
                                 'ALTCHA_HELP_MESSAGE',
                                 ''),
            'auto': getattr(settings, 'ALTCHA_AUTO', 'onload'),
        }
    )


@require_POST
def submit_challenge(request):
    """Attempt to validate Altcha challenge solution."""
    altcha_session_key = getattr(settings, 'ALTCHA_SESSION_KEY', 'altcha_verified')
    if time.time() <= request.session.get(altcha_session_key, 0):
        # User already passed Altcha verification and their approval hasn't expired yet.
        return JsonResponse({'success': True})
    try:
        payload = Payload.from_base64(request.POST.get('altcha'))
    except Exception:
        payload = {}
    result = verify_solution(
        payload, settings.ALTCHA_HMAC_KEY, hmac_key_secret=settings.ALTCHA_HMAC_KEY_SECRET)
    # If the solution validates and hasn't already been seen, create/update their session dam
    # expiration and store client IP address, as well as saving the challenge in cache.
    if (result.verified and not cache.get(payload.challenge.signature)):
        challenge_expire_mins = getattr(settings, 'ALTCHA_CHALLENGE_EXPIRE_MINUTES', 2)
        auth_expire_mins = getattr(settings, 'ALTCHA_AUTH_EXPIRE_MINUTES', 480)
        cache.set(
            payload.challenge.signature,
            't',
            timeout=challenge_expire_mins*60)
        altcha_session_key = getattr(settings, 'ALTCHA_SESSION_KEY', 'altcha_verified')
        request.session[altcha_session_key] = time.time() + auth_expire_mins*60
        # Store client IP address to verify on subsequent requests.
        request.session['ip'] = get_client_ip(request)
        return JsonResponse({'success': True})
    # Otherwise, reject them.
    fail_msg = getattr(settings, 'ALTCHA_FAIL_MESSAGE', 'Challenge failed or no longer valid.')
    return JsonResponse({'error': fail_msg}, status=400)
