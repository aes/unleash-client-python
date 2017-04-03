import datetime
import logging
import threading
import time

import requests

from .features import Feature
from .strategy import DEFAULT_STRATEGIES
from .util import FrozenDict

log = logging.getLogger(__name__)


def name_instance():
    import os
    import socket
    return "%s:%s" % (socket.gethostname(), os.getpid())


class PeriodicalOperation:
    def __init__(self, interval, clock=time.time):
        self.clock = clock
        self.interval = interval
        self.lock = threading.Lock()
        self.last = self.clock()
        self.cache = PeriodicalOperation
        self.log = log.getChild(self.__class__.__name__)

    def __call__(self):
        if self.cache == PeriodicalOperation:
            self.log.debug('first run')
            self.lock.acquire(True)
            self.run()
        now = self.clock()
        if now >= self.last + self.interval:
            if self.lock.acquire(False):
                self.log.info('got lock')
                threading.Thread(target=self.run).start()
        return self.cache


class Fetcher(PeriodicalOperation):
    def __init__(self, url, interval, clock=time.time):
        super().__init__(interval, clock)
        self.url = url
        self.etag = ''

    def run(self):
        # noinspection PyBroadException
        try:
            self.log.debug("ETag: %r", self.etag)
            headers = {'If-None-Match': self.etag}
            res = requests.get(url=self.url, headers=headers, timeout=3.0)

            if res.status_code == 304:
                self.log.debug("use cached value")
                return self.cache
            elif res.ok:
                self.log.debug("unpack new value")
                self.etag = res.headers['ETag']
                self.cache = res.json(object_hook=FrozenDict)
                return self.cache
            else:
                res.raise_for_status()
        except:
            log.exception("Exception fetching %r", self.url)
            if self.cache is PeriodicalOperation:
                self.cache = {}
            return self.cache
        finally:
            self.last = self.clock()
            self.lock.release()


class Reporter(PeriodicalOperation):
    def __init__(self, client, url, interval, clock=time.time):
        super().__init__(interval, clock)
        self.cache = None
        self.client = client
        self.url = url

    @staticmethod
    def fmt_time(t):
        return datetime.datetime.fromtimestamp(t).strftime('%FT%TZ')

    def run(self):
        # noinspection PyBroadException
        try:
            now = self.clock()
            start, stop, self.last = self.last, now, now
            bucket = {
                'start': self.fmt_time(start),
                'stop': self.fmt_time(stop),
                'toggles': {
                    name: feature.report()
                    for name, feature in self.client.features.items()
                },
            }

            report = {
                "appName": self.client.app_name,
                "instanceId": self.client.instance_id,
                "bucket": bucket,
            }
            self.log.info('%r', report)
            res = requests.post(self.url, json=report)
            self.log.info('%r', res.status_code)
        except:
            pass
        finally:
            self.lock.release()


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
    ):
        self.url = url
        self.app_name = app_name
        self.instance_id = instance_id or name_instance()

        self.strategies = strategies
        self.fetch = Fetcher(url + '/api/features', refresh_interval)
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
        defs = self.fetch()
        if defs is not self.defs:
            self.defs = defs
            ts = [Feature(self.strategies, f) for f in defs['features']]
            self.features = {t.feature['name']: t for t in ts}
        return self.features.get(name, lambda *al, **kw: False)

    def enabled(self, name, context):
        try:
            return self.get(name)(context)
        finally:
            self.reporter()

    def close(self):
        self.reporter()
