import datetime
import json
import logging
import threading
import time

import os
import requests

from .util import FrozenDict

log = logging.getLogger(__name__)


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


class UrlFetcher(PeriodicalOperation):
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
            if log.isEnabledFor(logging.DEBUG):
                log.debug("Exception fetching %r", self.url, exc_info=True)
            else:
                log.info("Exception fetching %r", self.url)

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


class FileFetcher:
    open_f = open
    stat_f = os.stat

    def __init__(self, path):
        self.cache = {}
        self.path = path
        self.last = 0

    def __call__(self):
        # noinspection PyBroadException
        try:
            st = self.stat_f(self.path)
            if st.st_mtime > self.last:
                with self.open_f(self.path) as fh:
                    self.cache = json.load(fh)
                self.last = st.st_mtime
        except:
            if log.isEnabledFor(logging.DEBUG):
                log.debug("Failed to read %r", self.path, exc_info=True)
            else:
                log.info("Failed to read %r")
        finally:
            return self.cache
