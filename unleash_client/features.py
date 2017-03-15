def feature_gates(strategies, feature):
    tests = []
    for args in feature['strategies']:
        name, parameters = args['name'], args['parameters']
        test = strategies[name](**parameters)
        tests.append(test)
    return tests


class Feature:
    def __init__(self, strategies, feature):
        self.feature = feature
        self.enabled = feature['enabled']
        self.choices = {False: 0, True: 0}
        self.gates = feature_gates(strategies, feature)

    def __call__(self, context):
        result = self.enabled and any(g(**context) for g in self.gates)
        self.choices[result] += 1
        return result

    def report(self):
        result, self.choices = self.choices, {False: 0, True: 0}
        return {'yes': result[True], 'no': result[False]}
