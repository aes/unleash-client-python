import random

from unittest import TestCase

from unleash_client.strategy import DEFAULT_STRATEGIES, normalize


class TestDefault(TestCase):
    def test_default_enabled(self):
        s = DEFAULT_STRATEGIES['default']
        assert s()


class TestNormalize(TestCase):
    def test_normalize(self):
        v = [normalize('a%d' % i, 'group') for i in range(10)]
        assert v == [59, 67, 9, 27, 69, 82, 53, 39, 76, 18]


class TestGradual(TestCase):
    t = DEFAULT_STRATEGIES['gradualRolloutUserId']('TEST', 25)

    def test_thumbs(self):
        v = [int(self.t(user_id='a%d' % i)) for i in range(10)]
        assert v == [0, 1, 0, 0, 1, 0, 0, 0, 0, 0]

    def test_field(self):
        v = ['1' if self.t(user_id='b%d' % i) else '0' for i in range(100)]
        b = [int('0b' + ''.join(v[i:i + 8]), 2) for i in range(0, 100, 8)]
        assert b == [
            0x02, 0x2c, 0x2c, 0x00,
            0x4d, 0x09, 0x18, 0xa4,
            0x01, 0x00, 0xc0, 0x02,
            0x00
        ]

    def test_distribution(self):
        v = [0, 0]

        for i in range(10000):
            v[self.t(user_id='c%d' % i)] += 1

        assert v == [7486, 2514]


class TestGradualRandom(TestCase):
    r = random.Random(x=1234)
    z = r.getstate()
    t = DEFAULT_STRATEGIES['gradualRolloutRandom'](25)
    t.die = r.randint

    def test_thumbs(self):
        self.r.setstate(self.z)
        v = [int(self.t()) for _ in range(10)]
        assert v == [0, 0, 1, 1, 1, 0, 1, 0, 0, 1]

    def test_field(self):
        self.r.setstate(self.z)
        v = ['1' if self.t() else '0' for _ in range(100)]
        b = [int('0b' + ''.join(v[i:i + 8]), 2) for i in range(0, 100, 8)]
        assert b == [
            0x3a, 0x63, 0x81, 0xd8,
            0x89, 0x24, 0x00, 0x5a,
            0x1c, 0xcc, 0xa2, 0x35,
            0x02,
        ]

    def test_distribution(self):
        self.r.setstate(self.z)
        v = [0, 0]

        for i in range(10000):
            v[self.t()] += 1

        assert v == [7517, 2483]


class TestExplicitSet(TestCase):
    t = DEFAULT_STRATEGIES['userWithId'](userIds='able,baker,cast')

    def test_included(self):
        assert self.t(user_id='able')

    def test_excluded(self):
        assert not self.t(user_id='easy')

    def test_absent(self):
        assert not self.t(cthulhu_for_president='why vote for a lesser evil?')
