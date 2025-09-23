from unittest.mock import patch
import base64
import json

import pytest
from django.conf import settings
from django.core.cache import cache


class TestDamChallengeView:
    """Unit tests for dam_challenge view."""

    def test_get_request_serves_challenge_page(self, client):
        """A GET request should serve the challenge page."""
        settings.ALTCHA_SALT_PARAMS = {'some': 'thing'}
        response = client.get('/dam/?next=%2Fprotected%2F')
        assert response.context['challenge'].max_number == settings.ALTCHA_MAX_NUMBER
        assert hasattr(response.context['challenge'], 'challenge')
        assert response.context['challenge'].salt.endswith('&some=thing')
        assert hasattr(response.context['challenge'], 'signature')
        assert response.status_code == 200
        assert ['dam_challenge.html'] == [a.name for a in response.templates]
        assert response.context['js_src_url'] == settings.ALTCHA_JS_URL
        assert response.context['site_icon_url'] == settings.ALTCHA_SITE_ICON_URL
        assert response.context['next_url'] == '/protected/'


class TestSubmitChallengeView:
    """Unit tests for submit_challenge view."""

    @pytest.mark.django_db
    @patch('dam.views.settings.ALTCHA_FAIL_MESSAGE', 'Sorry, please try again.')
    @patch('dam.views.verify_solution', return_value=[False, None])
    def test_post_request_fails_with_no_payload(self, mock_verify_solution, client):
        """A POST request with no payload should return a 400."""
        response = client.post('/dam/submit/')
        assert response.status_code == 400
        assert response.content.decode() == '{"error": "Sorry, please try again."}'
        mock_verify_solution.assert_called_once_with(
            {}, settings.ALTCHA_HMAC_KEY, check_expires=True)
        assert client.session.get(settings.ALTCHA_SESSION_KEY) is None

    @pytest.mark.django_db
    @patch('dam.views.time.time', return_value=1.0)
    @patch('dam.views.verify_solution', return_value=[True, None])
    def test_post_request_valid_challenge_response(self, mock_verify_solution, mock_time, client):
        """Valid POST request with good payload responds with success."""
        payload = {'challenge': '1234abcd'}
        payload_b64_encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        assert not cache.get(payload['challenge'])
        response = client.post('/dam/submit/', {'altcha': payload_b64_encoded,
                                                'next': '/protected/'})
        assert response.status_code == 200
        assert response.content.decode() == '{"success": true}'
        mock_verify_solution.assert_called_once_with(payload, settings.ALTCHA_HMAC_KEY,
                                                     check_expires=True)
        expected_auth_expiration = settings.ALTCHA_AUTH_EXPIRE_MINUTES * 60 + 1.0
        assert client.session[settings.ALTCHA_SESSION_KEY] == expected_auth_expiration
        assert cache.get(payload['challenge'])

    @pytest.mark.django_db
    @patch('dam.views.verify_solution', return_value=[False, None])
    def test_post_request_invalid_challenge_response(self, mock_verify_solution, client):
        """POST request with invalid challenge solution should return a 400 and failure message."""
        payload = {'challenge': '1234abcd'}
        payload_b64_encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        assert not cache.get(payload['challenge'])
        response = client.post('/dam/submit/', {'altcha': payload_b64_encoded,
                                                'next': '/protected/'})
        mock_verify_solution.assert_called_once_with(payload, settings.ALTCHA_HMAC_KEY,
                                                     check_expires=True)
        assert response.status_code == 400
        assert response.content.decode() == '{"error": "Challenge failed or no longer valid."}'
        assert client.session.get(settings.ALTCHA_SESSION_KEY) is None
        assert not cache.get(payload['challenge'])

    @pytest.mark.django_db
    @patch('dam.views.verify_solution', return_value=[True, None])
    def test_post_request_rejects_duplicate_challenge(self, mock_verify_solution, client):
        """POST request with valid but already-seen challenge solution is rejected."""
        payload = {'challenge': '1234abcd'}
        payload_b64_encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        cache.set(payload['challenge'], 't', timeout=settings.ALTCHA_AUTH_EXPIRE_MINUTES*60)
        response = client.post('/dam/submit/', {'altcha': payload_b64_encoded,
                                                'next': '/protected/'})
        mock_verify_solution.assert_called_once_with(payload, settings.ALTCHA_HMAC_KEY,
                                                     check_expires=True)
        assert response.status_code == 400
        assert response.content.decode() == '{"error": "Challenge failed or no longer valid."}'
        assert client.session.get(settings.ALTCHA_SESSION_KEY) is None
