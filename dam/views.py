import json
import time
import datetime
from base64 import b64decode


from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.core.cache import cache
from django.views.decorators.http import require_GET, require_POST
from altcha import create_challenge, verify_solution


@require_GET
def dam_challenge(request):
    """Provide user an Altcha challenge to solve before allowing access."""
    challenge_expire_mins = getattr(settings, 'ALTCHA_CHALLENGE_EXPIRE_MINUTES', 2)
    challenge = create_challenge(
        expires=datetime.datetime.now() + datetime.timedelta(minutes=challenge_expire_mins),
        max_number=settings.ALTCHA_MAX_NUMBER,
        hmac_key=settings.ALTCHA_HMAC_KEY,
        # Use the params to add arbitrary values to the salt, potentially increasing security
        params=getattr(settings, 'ALTCHA_SALT_PARAMS', {}),
    )
    next_url = request.GET.get('next', '/')
    return render(
        request,
        'dam_challenge.html',
        {
            'challenge': challenge,
            'site_icon_url': getattr(settings, 'ALTCHA_SITE_ICON_URL', ''),
            'js_src_url': getattr(
                settings, 'ALTCHA_JS_URL', f'{settings.STATIC_URL}altcha/altcha.min.js'),
            'css_src_url': getattr(
                settings, 'ALTCHA_CSS_URL', f'{settings.STATIC_URL}dam/dam.css'),
            'altcha_message': getattr(settings,
                                      'ALTCHA_MESSAGE',
                                      'Gauging your humanity...This may take some seconds.'),
            'next_url': next_url,
            'original_referrer': request.session.get(f'referer{next_url}', ''),
            'help_text': getattr(settings,
                                 'ALTCHA_HELP_MESSAGE',
                                 ''),
        }
    )


@require_POST
def submit_challenge(request):
    """Attempt to validate Altcha challenge solution."""
    try:
        payload = json.loads(b64decode(request.POST.get('altcha')))
    except Exception:
        payload = {}
    ok, err = verify_solution(payload, settings.ALTCHA_HMAC_KEY, check_expires=True)
    # If the solution validates and hasn't already been seen, create/update their session dam
    # expiration, as well as saving the challenge in cache.
    if (isinstance(payload, dict) and ok
            and not cache.get(payload.get('challenge'))):
        challenge_expire_mins = getattr(settings, 'ALTCHA_CHALLENGE_EXPIRE_MINUTES', 2)
        auth_expire_mins = getattr(settings, 'ALTCHA_AUTH_EXPIRE_MINUTES', 480)
        cache.set(
            payload['challenge'],
            't',
            timeout=challenge_expire_mins*60)
        altcha_session_key = getattr(settings, 'ALTCHA_SESSION_KEY', 'altcha_verified')
        request.session[altcha_session_key] = time.time() + auth_expire_mins*60
        # Remove no longer needed data from session.
        next_url = request.POST.get('next', ['/'])
        try:
            del request.session[f'referer{next_url}']
        except KeyError:
            pass
        return JsonResponse({'success': True})
    # Otherwise, reject them.
    fail_msg = getattr(settings, 'ALTCHA_FAIL_MESSAGE', 'Challenge failed or no longer valid.')
    return JsonResponse({'error': fail_msg}, status=400)
