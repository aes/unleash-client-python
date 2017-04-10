from unittest import mock, TestCase

from unleash_client import features


class TestFactory(TestCase):
    def test_simple_case(self):
        strategies = {'Foo': mock.Mock(return_value='R')}
        feature = {'strategies': [{'name': 'Foo', 'parameters': {'x': 0}}]}

        result = features.feature_gates(strategies, feature)

        assert result == ['R']
        assert strategies['Foo'].called_once_with(x=0)

    def test_two_strategies(self):
        strategies = {
            'Foo': mock.Mock(return_value='F'),
            'Bar': mock.Mock(return_value='B'),
        }
        feature = {'strategies': [
            {'name': 'Foo', 'parameters': {'x': 0}},
            {'name': 'Bar', 'parameters': {'y': 1}},
        ]}

        result = features.feature_gates(strategies, feature)

        assert result == ['F', 'B']
        assert strategies['Foo'].called_once_with(x=0)
        assert strategies['Bar'].called_once_with(y=1)

    def test_unknown_strategy(self):
        strategies = {}
        feature = {'strategies': [{'name': 'absent', 'parameters': {'z': 9}}]}

        with mock.patch('unleash_client.features.log') as log:
            result = features.feature_gates(strategies, feature)

        assert len(result) == 1
        assert callable(result[0])
        assert not result[0](basically_anything_here='foo')
        assert log.warning.called


class TestFeature(TestCase):
    def test_happy_path(self):
        strategies = {'Foo': mock.Mock(return_value=lambda z: z)}
        feature_def = {
            'enabled': True,
            'strategies': [{'name': 'Foo', 'parameters': {'x': 0}}],
        }

        toggle = features.Feature(strategies, feature_def)

        assert isinstance(toggle, features.Feature)
        assert toggle({'z': True})
        assert not toggle({'z': False})
        assert toggle.choices == {True: 1, False: 1}

    def test_empty_strategy_list(self):
        strategies = {'Foo': mock.Mock(return_value=lambda z: z)}
        feature_def = {
            'enabled': True,
            'strategies': [],
        }

        toggle = features.Feature(strategies, feature_def)

        assert isinstance(toggle, features.Feature)
        assert not toggle({'z': True})
        assert not toggle({'z': False})
        assert toggle.choices == {True: 0, False: 2}

    def test_disable(self):
        strategies = {'Foo': mock.Mock(return_value=lambda z: z)}
        feature_def = {
            'enabled': False,
            'strategies': [{'name': 'Foo', 'parameters': {'x': 0}}],
        }

        toggle = features.Feature(strategies, feature_def)

        assert not toggle({'z': True})
        assert not toggle({'z': False})
        assert toggle.choices == {True: 0, False: 2}
