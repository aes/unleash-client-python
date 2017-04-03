from requests import exceptions
from unittest import mock, TestCase

import unleash_client


class TestFetch(TestCase):
    @mock.patch('unleash_client.requests')
    def test_happy_path(self, requests):
        requests.get.side_effect = exceptions.ConnectionError
        c = unleash_client.Client()
        assert not c.enabled('foo', {})
