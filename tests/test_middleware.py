from unittest.mock import patch, Mock
from ipaddress import ip_network
from time import time

from django.conf import settings
from django.urls import reverse
import pytest

from dam.middleware import AltchaMiddleware, make_ip_list


class TestAltchaMiddleware:
    @patch('dam.middleware.make_ip_list', return_value=[ip_network('1.2.0.0/16'),
                                                        ip_network('127.0.0.1/32')])
    def test_init(self, mock_make_ip_list):
        mock_get_response = Mock()
        AM = AltchaMiddleware(mock_get_response)
        assert AM.get_response == mock_get_response
        assert AM.altcha_session_key == settings.ALTCHA_SESSION_KEY
        assert AM.excluded_paths == settings.ALTCHA_EXCLUDE_PATHS
        mock_make_ip_list.assert_called_once_with(settings.ALTCHA_EXCLUDE_IPS)
        assert AM.excluded_ips == mock_make_ip_list.return_value

    @pytest.mark.parametrize('current_ip, expected', [
        ('127.0.0.1', True), # Exact IP excluded
        ('1.2.3.4', True),   # IP excluded in network
        ('1.1.1.1', False),  # IP before excluded range
        ('2.2.2.2', False),  # IP after excluded range
    ])
    @patch('dam.middleware.make_ip_list', Mock(return_value=[ip_network('1.2.0.0/16'),
                                                             ip_network('127.0.0.1/32')]))
    def test_exclude_ip(self, current_ip, expected, rf):
        mock_get_response = Mock()
        AM = AltchaMiddleware(mock_get_response)
        request = rf.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = current_ip
        assert AM.exclude_ip(request) == expected

    @patch('dam.middleware.make_ip_list', Mock(return_value=[]))
    def test_exclude_ip_no_excluded_networks(self, rf):
        mock_get_response = Mock()
        AM = AltchaMiddleware(mock_get_response)
        request = rf.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        assert AM.exclude_ip(request) == False
    
    def test_exclude_ip_invalid_ip_address(self, rf):
        mock_get_response = Mock()
        AM = AltchaMiddleware(mock_get_response)
        request = rf.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = ''
        assert AM.exclude_ip(request) == False

    @pytest.mark.parametrize('forwarded_for, remote_addr, expected_ip', [
        ('1.1.1.1, 2.2.2.2', None, '1.1.1.1'),
        ('1.1.1.1, 2.2.2.2', '3.3.3.3, 4.4.4.4', '1.1.1.1'),
        (None, '3.3.3.3, 4.4.4.4', '3.3.3.3'),
    ])
    @patch('dam.middleware.ipaddress.ip_address', side_effect=ValueError)
    @patch('dam.middleware.make_ip_list', Mock(return_value=[ip_network('1.2.0.0/16'),
                                                             ip_network('127.0.0.1/32')]))
    def test_exclude_ip_uses_expected_ip(self, mock_ip_address, forwarded_for, remote_addr,
                                         expected_ip, rf):
        mock_get_response = Mock()
        AM = AltchaMiddleware(mock_get_response)
        request = rf.get('/')
        if forwarded_for:
            request.META['HTTP_X_FORWARDED_FOR'] = forwarded_for
        if remote_addr:
            request.META['REMOTE_ADDR'] = remote_addr
        AM.exclude_ip(request)
        mock_ip_address.assert_called_once_with(expected_ip)

    @pytest.mark.django_db
    def test_process_request_user_exempt(self, rf):
        mock_get_response = Mock()
        AM = AltchaMiddleware(mock_get_response)
        request = rf.get('/protected_page')
        request.session = {settings.ALTCHA_SESSION_KEY: time()+100}
        assert AM.process_request(request) is None

    @pytest.mark.django_db
    @pytest.mark.parametrize('path', [
        reverse('dam:challenge'), # We never add another challenge to the challenge page
        '/some_safe_page' # Set as an excluded path in the test
    ])
    def test_process_request_path_exempt(self, path, rf):
        mock_get_response = Mock()
        AM = AltchaMiddleware(mock_get_response)
        AM.excluded_paths = ['/some_safe_page']
        request = rf.get(path)
        request.session = {}
        assert AM.process_request(request) is None

    @pytest.mark.django_db
    @patch('dam.middleware.make_ip_list', Mock(return_value=[ip_network('127.0.0.1/32')]))
    def test_process_request_ip_exempt(self, rf):
        mock_get_response = Mock()
        AM = AltchaMiddleware(mock_get_response)
        AM.exclude_ip = Mock(return_value=True)
        request = rf.get('/protected_page')
        request.session = {}
        request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1' # Explicitly excluded
        assert AM.process_request(request) is None
        AM.exclude_ip.assert_called_once_with(request)
    
    @pytest.mark.django_db
    def test_process_request_challenge_user(self, rf):
        mock_get_response = Mock()
        AM = AltchaMiddleware(mock_get_response)
        AM.exclude_ip = Mock(return_value=False)
        request = rf.get('/protected_page?search=stuff')
        request.session = {}
        response = AM.process_request(request)
        assert response.status_code == 302
        assert response.url == reverse('dam:challenge')+'?next=%2Fprotected_page%3Fsearch%3Dstuff'


class TestMakeIPList:
    def test_make_ip_list(self, capsys):
        ip_addresses = ['1.2.0.0/16', '127.0.0.1', 'not_an_ip_address']
        expected = [ip_network('1.2.0.0/16'), ip_network('127.0.0.1')]
        assert make_ip_list(ip_addresses) == expected
        assert capsys.readouterr().out.startswith('Could not exclude supplied ip address')