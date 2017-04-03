import logging

from .clients import Client, DummyClient
from .io import UrlFetcher, FileFetcher

log = logging.getLogger(__name__)


def client(
    url='',
    refresh_interval=60,
    fetch=None,
    *al,
    **kw
):
    if fetch:
        pass
    elif not url:
        return DummyClient()
    elif ':' not in url:
        fetch = FileFetcher(url)
    elif url.startswith('file:///'):
        fetch = FileFetcher(url[8:])
    elif url.startswith('http://') or url.startswith('https://'):
        fetch = UrlFetcher(url + '/api/features', refresh_interval)
    else:
        log.error("Unexpected unleash client url scheme: %r", url)
        raise ValueError(url)

    return Client('', *al, fetch=fetch, **kw)
