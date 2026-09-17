from unittest.mock import patch, Mock
import base64
import json

import altcha
import pytest
from django.conf import settings
from django.core.cache import cache


class TestDamChallengeView:
    """Unit tests for dam_challenge view."""

    def test_get_request_serves_challenge_page(self, client):
        """A GET request should serve the challenge page."""
        response = client.get('/dam/?next=%2Fprotected%2F')
        challenge = altcha.Challenge.from_dict(json.loads(response.context['challenge']))
        assert challenge.parameters.cost == settings.ALTCHA_COST
        assert response.status_code == 200
        assert ['dam_challenge.html'] == [a.name for a in response.templates]
        assert response.context['js_src_url'] == settings.ALTCHA_JS_URL
        assert response.context['css_src_url'] == settings.ALTCHA_CSS_URL
        assert response.context['site_icon_url'] == settings.ALTCHA_SITE_ICON_URL
        assert response.context['next_url'] == '/protected/'


@pytest.mark.django_db
class TestSubmitChallengeView:
    """Unit tests for submit_challenge view."""

    @patch('dam.views.settings.ALTCHA_FAIL_MESSAGE', 'Sorry, please try again.')
    @patch('dam.views.verify_solution', return_value=Mock(verified=False))
    def test_post_request_fails_with_no_payload(self, mock_verify_solution, client):
        """A POST request with no payload should return a 400."""
        response = client.post('/dam/submit/')
        assert response.status_code == 400
        assert response.content.decode() == '{"error": "Sorry, please try again."}'
        mock_verify_solution.assert_called_once_with(
            {}, settings.ALTCHA_HMAC_KEY, hmac_key_secret=settings.ALTCHA_HMAC_KEY_SECRET)
        assert client.session.get(settings.ALTCHA_SESSION_KEY) is None

    @patch('dam.views.time.time', return_value=1.0)
    @patch('dam.views.Payload.from_base64',
           return_value=Mock(challenge=Mock(signature='1234abcd')))
    @patch('dam.views.verify_solution', return_value=Mock(verified=True))
    def test_post_request_valid_challenge_response(
            self, mock_verify_solution, mock_payload_from_base64, mock_time, client):
        """Valid POST request with good payload responds with success."""
        payload = {'challenge': {'signature': '1234abcd'}}
        payload_b64_encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        assert not cache.get(payload['challenge']['signature'])
        response = client.post('/dam/submit/', {'altcha': payload_b64_encoded,
                                                'next': '/protected/'})
        assert response.status_code == 200
        assert response.content.decode() == '{"success": true}'
        mock_verify_solution.assert_called_once_with(
            mock_payload_from_base64.return_value,
            settings.ALTCHA_HMAC_KEY,
            hmac_key_secret=settings.ALTCHA_HMAC_KEY_SECRET)
        expected_auth_expiration = settings.ALTCHA_AUTH_EXPIRE_MINUTES * 60 + 1.0
        assert client.session[settings.ALTCHA_SESSION_KEY] == expected_auth_expiration
        assert cache.get(payload['challenge']['signature'])

    @patch('dam.views.Payload.from_base64',
           return_value=Mock(challenge=Mock(signature='1234abcd')))
    @patch('dam.views.verify_solution', return_value=Mock(verified=False))
    def test_post_request_invalid_challenge_response(
            self, mock_verify_solution, mock_payload_from_base64, client):
        """POST request with invalid challenge solution should return a 400 and failure message."""
        payload = {'challenge': {'signature': '1234abcd'}}
        payload_b64_encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        assert not cache.get(payload['challenge']['signature'])
        response = client.post('/dam/submit/', {'altcha': payload_b64_encoded,
                                                'next': '/protected/'})
        assert response.status_code == 400
        assert response.content.decode() == '{"error": "Challenge failed or no longer valid."}'
        mock_verify_solution.assert_called_once_with(
            mock_payload_from_base64.return_value,
            settings.ALTCHA_HMAC_KEY,
            hmac_key_secret=settings.ALTCHA_HMAC_KEY_SECRET)
        assert client.session.get(settings.ALTCHA_SESSION_KEY) is None
        assert not cache.get(payload['challenge']['signature'])

    @patch('dam.views.Payload.from_base64',
           return_value=Mock(challenge=Mock(signature='1234abcd')))
    @patch('dam.views.verify_solution', return_value=Mock(verified=False))
    def test_post_request_rejects_duplicate_challenge(
            self, mock_verify_solution, mock_payload_from_base64, client):
        """POST request with valid but already-seen challenge solution is rejected."""
        payload = {'challenge': {'signature': '1234abcd'}}
        payload_b64_encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        cache.set(
            payload['challenge']['signature'],
            't',
            timeout=settings.ALTCHA_AUTH_EXPIRE_MINUTES*60)
        response = client.post('/dam/submit/', {'altcha': payload_b64_encoded,
                                                'next': '/protected/'})
        assert response.status_code == 400
        assert response.content.decode() == '{"error": "Challenge failed or no longer valid."}'
        mock_verify_solution.assert_called_once_with(
            mock_payload_from_base64.return_value,
            settings.ALTCHA_HMAC_KEY,
            hmac_key_secret=settings.ALTCHA_HMAC_KEY_SECRET)
        assert client.session.get(settings.ALTCHA_SESSION_KEY) is None

    @patch('dam.views.time.time', return_value=1.0)
    @patch('dam.views.verify_solution')
    def test_post_request_pass_already_validated_user(self, mock_verify_solution, mock_time,
                                                      client):
        """POST request for already-validated user succeeds regardless of challenge response."""
        # Make sure the client shows as being validated
        auth_expiration = settings.ALTCHA_AUTH_EXPIRE_MINUTES * 60 + 1.0
        # Test client session _must_ be stored in a var for changes to take effect.
        session = client.session
        session[settings.ALTCHA_SESSION_KEY] = auth_expiration
        session.save()
        response = client.post('/dam/submit/', {'altcha': 'not even trying',
                                                'next': '/protected/'})
        assert response.status_code == 200
        assert response.content.decode() == '{"success": true}'
        # We don't even want to check the solution if the user's already validated
        mock_verify_solution.assert_not_called()
