import time

import logging

from .strategy import DEFAULT_STRATEGIES
from .io import UrlFetcher, Reporter
from .features import Feature

log = logging.getLogger(__name__)


def name_instance():
    import os
    import socket
    return "%s:%s" % (socket.gethostname(), os.getpid())


class Client:
    def __init__(
            self,
            url='http://localhost:4242',
            app_name='anon-app',
            instance_id=None,
            refresh_interval=60,
            metrics_interval=60,
            disable_metrics=False,
            strategies=DEFAULT_STRATEGIES,
            clock=time.time,
            fetch=None,
    ):
        self.url = url
        self.app_name = app_name
        self.instance_id = instance_id or name_instance()

        self.strategies = strategies
        self.fetch = fetch or UrlFetcher(url + '/api/features', refresh_interval)
        self.defs = {}
        self.features = {}

        if not disable_metrics:
            self.reporter = Reporter(
                self,
                url + '/api/client/metrics',
                metrics_interval,
                clock=clock,
            )
        else:
            self.reporter = lambda *al: None

    def get(self, name):
        d = self.fetch()
        if d is not self.defs:
            self.defs = d
            ts = [Feature(self.strategies, f) for f in d.get('features', [])]
            self.features = {t.feature['name']: t for t in ts}
        return self.features.get(name, lambda *al, **kw: False)

    def enabled(self, name, context):
        try:
            return self.get(name)(context)
        finally:
            self.reporter()

    def close(self):
        self.reporter()


class DummyClient:
    enabled = staticmethod(lambda name, context: False)
    close = staticmethod(lambda: None)
