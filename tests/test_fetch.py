from requests import exceptions, Response
from unittest import mock, TestCase

from unleash_client import client, DummyClient, FileFetcher

example = {
    'features': [{
        'enabled': True,
        'name': 'foo',
        'strategies': [{'parameters': {}, 'name': 'default'}],
    }],
}
example_json = (
    '{"features":[{'
    '"enabled":true,'
    '"name":"foo",'
    '"strategies":[{"parameters":{},"name":"default"}]}]}'
)


class TestDummyClient(TestCase):
    def test_blank_config(self):
        c = client()
        assert isinstance(c, DummyClient)
        assert not client().enabled('foo', {})


class TestUrlFetch(TestCase):
    url = 'http://example.com/api/features'

    @mock.patch('unleash_client.io.requests')
    def test_url_to_nowhere(self, requests):
        requests.get.side_effect = exceptions.ConnectionError
        assert not client(url=self.url).enabled('foo', {})

    @mock.patch('unleash_client.io.requests')
    def test_fetchable_url(self, requests):
        requests.get.return_value = r = mock.Mock(wraps=Response())
        r.ok = True
        r.status_code = 200
        r.headers = {'ETag': 'e-tag'}
        r.json.return_value = {
            'features': [{
                'name': 'foo',
                'enabled': True,
                'strategies': [{'name': 'default', 'parameters': {}}],
            }],
        }
        c = client(url=self.url)
        assert c.enabled('foo', {})
        assert r.json.called


class TestFileFetch(TestCase):
    def test_file_url(self):
        c = client(url='path/to/file')
        assert isinstance(c.fetch, FileFetcher)

    def test_file_fetch(self):
        c = client(url='path/to/file')

        c.fetch.open_f = o = mock.MagicMock()
        o.return_value.__enter__.return_value.read.return_value = example_json

        c.fetch.stat_f = s = mock.Mock()
        s.return_value.st_mtime = 12

        assert c.enabled('foo', {})
        assert s.called
        assert o.return_value.__enter__.called

    def test_file_stat_fail(self):
        c = client(url='path/to/file')

        c.fetch.open_f = o = mock.MagicMock()
        o.return_value.__enter__.return_value.read.return_value = example_json

        c.fetch.stat_f = s = mock.Mock()
        s.return_value.side_effect = FileNotFoundError

        assert not c.enabled('foo', {})
        assert s.called
        assert not o.return_value.__enter__.called

    def test_file_open_fail(self):
        c = client(url='path/to/file')

        c.fetch.open_f = o = mock.MagicMock()
        o.return_value.side_effect = FileNotFoundError

        c.fetch.stat_f = s = mock.Mock()
        s.return_value.st_mtime = 12

        assert not c.enabled('foo', {})
        assert s.called
        assert o.called

    def test_file_parse_fail(self):
        c = client(url='path/to/file')

        c.fetch.open_f = o = mock.MagicMock()
        o.return_value.__enter__.return_value.read.return_value = 'not-json'

        c.fetch.stat_f = s = mock.Mock()
        s.return_value.st_mtime = 12

        assert not c.enabled('foo', {})
        assert s.called
        assert o.called
