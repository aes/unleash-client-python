import random
from hashlib import md5

from .util import FrozenDict


def normalize(key, group):
    value = '%s:%s' % (group, key)
    end = md5(value.encode('utf-8')).hexdigest()[-4:]
    return int(end, 16) % 100


class Default:
    def __call__(self, **kw):
        return True


class GradualRolloutRandom:
    die = random.randint

    def __init__(self, percentage=0, **kw):
        self.percentage = int(percentage)

    def __call__(self, **kw):
        return self.die(0, 99) < self.percentage


class GradualRolloutFactory:
    def __init__(self, key):
        self.key = key

    def __call__(self, groupId, percentage):
        def test(anonymous_arg='', **kw):
            key = kw.get(test.key, anonymous_arg)
            norm = normalize(key, test.group_id)
            return norm < test.percentage
        test.key = self.key
        test.group_id = groupId
        test.percentage = int(percentage or '0')
        return test


class ExplicitSetFactory:
    def __init__(self, parameter, key=None):
        self.parameter = parameter
        self.key = key or parameter

    def __call__(self, members='', **kw):
        def test(anonymous_arg='', **kw):
            key = kw.get(test.key, anonymous_arg)
            return key in test.members
        test.key = self.key
        test.members = set(kw.get(self.parameter, members).split(','))
        return test


DEFAULT_STRATEGIES = FrozenDict(**{
    'applicationHostname': ExplicitSetFactory('hostNames', 'host'),
    'default': Default,
    'gradualRolloutRandom': GradualRolloutRandom,
    'gradualRolloutSessionId': GradualRolloutFactory('session_id'),
    'gradualRolloutUserId': GradualRolloutFactory('user_id'),
    'remoteAddress': ExplicitSetFactory('IPs', 'remote_addr'),
    'userWithId': ExplicitSetFactory('userIds', 'user_id'),
})
