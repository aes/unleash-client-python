import argparse
import random
import logging
import time

from unleash_client import client

argparser = argparse.ArgumentParser(
    'unleash', description='Unleash test client',
)

argparser.add_argument(
    '-v', '--verbose',
    action='count',
    default=0,
)

argparser.add_argument(
    '-u', '--url',
    default='http://localhost:4242',
    help='URL base for the Unleash feature toggle service',
)

argparser.add_argument(
    '-d', '--demo',
    action='store_true',
    help='Loop thrashing demo mode instead of lookup',
)

argparser.add_argument(
    '-s', '--sleep',
    default='0.1',
    type=float,
    help='Time for demo to sleep between checks',
)

argparser.add_argument(
    'feature',
    default='feature',
    help='Feature to test',
)

argparser.add_argument(
    'attrs',
    nargs='*',
    help='Attributes of the form key=val',
)


def demo_it(client, feature_name, context, sleep=0):
    try:
        while True:
            x = ''.join(chr(random.randint(33, 126)) for i in range(6))
            current = {k: (x if v == '%' else v) for k, v in context.items()}
            result = client.enabled(feature_name, context=current)
            blip = '.|'[result]
            print(blip, end='')
            sys.stdout.flush()
            if sleep:
                time.sleep(sleep)
    except KeyboardInterrupt:
        client.close()


def main(args):
    ns = argparser.parse_args(args[1:])

    logging.basicConfig()
    logging.getLogger().setLevel(10 * max(1, 3 - ns.verbose))

    un = client(
        url=ns.url,
        refresh_interval=5,
        metrics_interval=2,
    )
    context = dict(kv.split('=') for kv in ns.attrs)

    if ns.demo:
        demo_it(un, ns.feature, context, ns.sleep)
    else:
        result = un.enabled(ns.feature, context)
        print('yes' if result else 'no')


if __name__ == '__main__':
    import sys
    raise sys.exit(main(tuple(sys.argv)) or 0)
